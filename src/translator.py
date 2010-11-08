
import rtmidi


import core
from log import Logger

class Translator(object):
    
    def __init__(self, options):
        
        print "create translator"
        pass
    
    def process(self, channel, msg):
        pass
    
    def send(self, channel, msg):
        channel.send(msg)
    

class TranslatorFactory(object):
    
    translators = {}
    
    @classmethod
    def register(cls, translator):
        Logger.debug("Registering translator class '%s'" % (translator.__name__))
        cls.translators[translator.__name__] = translator
    
    @classmethod
    def create(cls, name, options):
        Logger.debug("Creating translator class '%s' using options: %s" % (name, options))
        return cls.translators[name](options)

    
class TranslatorFx(Translator):
    
    STATE_NORMAL = 0
    STATE_MUTE = 1
    STATE_FX1 = 2
    STATE_FX2 = 3
    
    state_names = {
        STATE_NORMAL    : 'Normal',
        STATE_MUTE      : 'Mute',
        STATE_FX1       : 'FX1',
        STATE_FX2       : 'FX2',
    }
    
    def __init__(self, options):
        self.controller = core.Core.instance().get_channel_by_name(options['controller'])
        self.host = core.Core.instance().get_channel_by_name(options['host'])
        
        self.__key_map = {
            int(options['note_key1']) : self.__key1_handler,
            int(options['note_key2']) : self.__key2_handler,
            int(options['note_key3']) : self.__key3_handler,
        }
        self.__master = int(options['cc_master'])
        self.__send1 = int(options['cc_send1'])
        self.__send2 = int(options['cc_send2'])
        self.__state = self.STATE_NORMAL
        
    def process(self, channel, msg):
        if channel != self.controller:
            return

        if msg.isNoteOn() and msg.getNoteNumber() in self.__key_map:
            self.__key_map[msg.getNoteNumber()]()
            self.__update()
            
    def __key1_handler(self):
        if self.__state == self.STATE_NORMAL:
            self.__state = self.STATE_MUTE
        else:
            self.__state = self.STATE_NORMAL
    
    def __key2_handler(self):
        self.__state = self.STATE_FX1
    
    def __key3_handler(self):
        self.__state = self.STATE_FX2
        
    def __update(self):
        print self.state_names[self.__state]

        if self.__state == self.STATE_NORMAL:
            self.__update_levels(127, 0, 0)
        elif self.__state == self.STATE_MUTE:
            self.__update_levels(0, 0, 0)
        elif self.__state == self.STATE_FX1:
            self.__update_levels(0, 127, 0)
        elif self.__state == self.STATE_FX2:
            self.__update_levels(0, 0, 127)
        
    def __update_levels(self, master, send1, send2):
        self.host.send(rtmidi.MidiMessage.controllerEvent(1, self.__master, master))
        self.host.send(rtmidi.MidiMessage.controllerEvent(1, self.__send1, send1))
        self.host.send(rtmidi.MidiMessage.controllerEvent(1, self.__send2, send2))


TranslatorFactory.register(TranslatorFx)


class TranslatorLooper(Translator):
    
    STATE_CLEAR = 0
    STATE_PLAY = 1
    STATE_OVERDUB = 2
    STATE_IDLE = 3
    
    state_names = {
        STATE_CLEAR : 'clear',
        STATE_PLAY : 'play',
        STATE_OVERDUB : 'overdub',
        STATE_IDLE : 'idle',
    }
    
    def __init__(self, options):
        self.controller = core.Core.instance().get_channel_by_name(options['controller'])
        self.host = core.Core.instance().get_channel_by_name(options['host'])
        
        self.__key_map = {
            int(options['note_key1']) : self.__key1_handler,
            int(options['note_key2']) : self.__key2_handler,
            int(options['note_key3']) : self.__key3_handler,
            int(options['note_key4']) : self.__key4_handler,
            int(options['note_key5']) : self.__key5_handler,
        }
        
        self.__leds = [
            int(options['note_led1']),
            int(options['note_led2']),
            int(options['note_led3']),
            int(options['note_led4']),
        ]
        
        self.__cmd_map = {
            'focus' : int(options['note_focus']),
            'rec_add' : int(options['note_rec_add']),
            'play' : int(options['note_play']),
            'stop' : int(options['note_stop']),
            'clear' : int(options['note_clear']),
            'half' : int(options['note_half']),
            'double' : int(options['note_double']),
            'undo_redo' : int(options['note_undo_redo']),
        }
        
        self.__state = self.STATE_CLEAR

    def process(self, channel, msg):
        if channel != self.controller:
            return

        if msg.isNoteOn() and msg.getNoteNumber() in self.__key_map:
            self.__key_map[msg.getNoteNumber()]()
            
    def __key1_handler(self):
        print "Key 1"
        print "Entry state: %s" % (self.state_names[self.__state])
        self.__send_cmd('focus')
        if self.__state == self.STATE_CLEAR:
            # Start recording and switch to PLAY state
            self.__send_cmd('rec_add')
            self.__set_led(1, True)
            self.__state = self.STATE_PLAY
        elif self.__state == self.STATE_PLAY:
            # Start overdub recording and switch to OVERDUB state
            self.__send_cmd('rec_add')
            self.__set_led(0, True)
            self.__state = self.STATE_OVERDUB
        elif self.__state == self.STATE_OVERDUB:
            # Stop overdub recording and switch to PLAY state
            self.__send_cmd('play')
            self.__set_led(0, False)
            self.__state = self.STATE_PLAY
        elif self.__state == self.STATE_IDLE:
            # Start playback and switch to PLAY state
            self.__send_cmd('play')
            self.__state = self.STATE_PLAY
        print "Exit state: %s" % (self.state_names[self.__state])

    def __key2_handler(self):
        print "Key 2"
        print "Entry state: %s" % (self.state_names[self.__state])
        self.__send_cmd('focus')
        if self.__state == self.STATE_CLEAR:
            # Clear recording
            self.__send_cmd('clear')
            self.__set_led(0, False)
            self.__set_led(1, False)
        elif self.__state == self.STATE_PLAY:
            # Stop playback and switch to IDLE state
            self.__send_cmd('stop')
            self.__state = self.STATE_IDLE
        elif self.__state == self.STATE_OVERDUB:
            # Stop overdub recording and switch to IDLE state
            self.__send_cmd('stop')
            self.__set_led(0, False)
            self.__state = self.STATE_IDLE
        elif self.__state == self.STATE_IDLE:
            # Clear recording and switch to CLEAR state
            self.__send_cmd('clear')
            self.__set_led(0, False)
            self.__set_led(1, False)
            self.__state = self.STATE_CLEAR
        print "Exit state: %s" % (self.state_names[self.__state])

    def __key3_handler(self):
        print "Key 3"
        self.__send_cmd('focus')
        self.__send_cmd('half')

    def __key4_handler(self):
        print "Key 4"
        self.__send_cmd('focus')
        self.__send_cmd('double')
        
    def __key5_handler(self):
        print "Key 5"
        self.__send_cmd('focus')
        self.__send_cmd('undo_redo')
        
    def __send_cmd(self, cmd):
        self.host.send(rtmidi.MidiMessage.noteOn(1, self.__cmd_map[cmd], 127))
        self.host.send(rtmidi.MidiMessage.noteOff(1, self.__cmd_map[cmd]))
        
    def __set_led(self, led, on):
        if on:
            self.controller.send(rtmidi.MidiMessage.noteOn(1, self.__leds[led], 127))
        else:
            self.controller.send(rtmidi.MidiMessage.noteOff(1, self.__leds[led]))

TranslatorFactory.register(TranslatorLooper)



class TranslatorSource(Translator):
    
    def __init__(self, options):
        self.controller = core.Core.instance().get_channel_by_name(options['controller'])
        self.host = core.Core.instance().get_channel_by_name(options['host'])
        
        self.__key_map = {
            int(options['note_key1']) : self.__key1_handler,
            int(options['note_key2']) : self.__key2_handler,
            int(options['note_key3']) : self.__key3_handler,
            int(options['note_key4']) : self.__key4_handler,
        }

        self.__channels = [
            int(options['cc_channel1']),
            int(options['cc_channel2']),
            int(options['cc_channel3']),
            int(options['cc_channel4']),
        ]
        
        self.__selector = int(options['cc_selector'])
        self.__focus = int(options['note_focus'])

        self.__source = 0
        
    def process(self, channel, msg):
        if channel != self.controller:
            return

        if msg.isNoteOn() and msg.getNoteNumber() in self.__key_map:
            self.__key_map[msg.getNoteNumber()]()
            self.__update()
            
    def __key1_handler(self):
        self.__source = 0
    
    def __key2_handler(self):
        self.__source = 1
    
    def __key3_handler(self):
        self.__source = 2
        
    def __key4_handler(self):
        self.__source = 3
        
    def __update(self):
        index = 0
        for channel in self.__channels:
            if index == self.__source:
                self.host.send(rtmidi.MidiMessage.controllerEvent(1, channel, 127))
            else:
                self.host.send(rtmidi.MidiMessage.controllerEvent(1, channel, 0))
            index += 1
        self.host.send(rtmidi.MidiMessage.controllerEvent(1, self.__selector, self.__source * (127.0 / 3)))
        self.host.send(rtmidi.MidiMessage.noteOn(1, self.__focus, 127))
        self.host.send(rtmidi.MidiMessage.noteOff(1, self.__focus))


TranslatorFactory.register(TranslatorSource)



class TranslatorRepeat(Translator):
    
    MIN_VALUE = 0
    MAX_VALUE = 10
    
    def __init__(self, options):
        self.controller = core.Core.instance().get_channel_by_name(options['controller'])
        self.host = core.Core.instance().get_channel_by_name(options['host'])
        
        self.__key_map = {
            int(options['note_key1']) : self.__key1_handler,
            int(options['note_key2']) : self.__key2_handler,
            int(options['note_key3']) : self.__key3_handler,
            int(options['note_key4']) : self.__key4_handler,
            int(options['note_key5']) : self.__key5_handler,
            int(options['note_key6']) : self.__key6_handler,
        }

        self.__leds = [
            int(options['note_led1']),
            int(options['note_led2']),
            int(options['note_led3']),
            int(options['note_led4']),
        ]

        self.__value = self.MIN_VALUE
        
    def process(self, channel, msg):
        if channel != self.controller:
            return

        if msg.isNoteOn() and msg.getNoteNumber() in self.__key_map:
            self.__key_map[msg.getNoteNumber()]()
            self.__update()
            
    def __key1_handler(self):
        self.__value = 0
    
    def __key2_handler(self):
        self.__value = 1
    
    def __key3_handler(self):
        self.__value = 2
        
    def __key4_handler(self):
        self.__value = 3
        
    def __key5_handler(self):
        if self.__value > self.MIN_VALUE:
            self.__value = self.__value - 1
        
    def __key6_handler(self):
        if self.__value < self.MAX_VALUE:
            self.__value = self.__value + 1
        
    def __update(self):
        active = self.__value - self.MIN_VALUE
        for index in range(len(self.__leds)):
            led = self.__leds[index]
            if index == active:
                self.controller.send(rtmidi.MidiMessage.noteOn(1, led, 127))
            else:
                self.controller.send(rtmidi.MidiMessage.noteOff(1, led))


TranslatorFactory.register(TranslatorRepeat)
