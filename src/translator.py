
import rtmidi


import core
from log import Logger

class Translator(object):
    
    def __init__(self, options):
        
        self.__key_map = {}
        self.__cmd_map = {}
        self.__led_map = {}
        self.__ctrl_map = {}
            
    def process(self, channel, msg):
        """
        Called for incoming MIDI messages. Calls the registered key handlers.
        """
        if msg.isNoteOn():
            try:
                info = self.__key_map[channel][msg.getNoteNumber()]
                info['handler'](info['key'])
            except KeyError:
                pass
    
    def send(self, channel, msg):
        channel.send(msg)
        
    def add_key(self, key, handler, channel, note):
        """
        Adds a key handler to the translator. The key handler is triggered
        when receiving the specified note on the given channel.
        """
        try:
            channel_map = self.__key_map[channel]
        except KeyError:
            channel_map = {}
            self.__key_map[channel] = channel_map
        channel_map[note] = { 'key': key, 'handler': handler }
        
    def add_cmd(self, cmd, channel, note):
        """
        Adds a command to the translator. When sending the command using
        send_cmd() a note on/off is sent using the specified note on the
        given channel.
        """
        self.__cmd_map[cmd] = { 'channel': channel, 'note': note }
        pass
    
    def add_led(self, led, channel, note):
        """
        Adds a LED to the translator. When setting the LED using set_led()
        a note on/off is sent using the specified note on the given channel.
        """
        self.__led_map[led] = { 'channel': channel, 'note': note }
    
    def add_ctrl(self, ctrl, channel, cc):
        """
        Adds a controller to the translator. When sending a controller value
        using send_ctrl() a CC is sent using the specified CC number on the
        given channel.
        """
        self.__ctrl_map[ctrl] = { 'channel': channel, 'cc': cc }
    
    def send_cmd(self, cmd):
        """
        Sends a command. This will send a note on followed by note off event.
        """
        channel = self.__cmd_map[cmd]['channel']
        note = self.__cmd_map[cmd]['note']
        channel.send(rtmidi.MidiMessage.noteOn(1, note, 127))
        channel.send(rtmidi.MidiMessage.noteOff(1, note))
    
    def set_led(self, led, on):
        """
        Sets a LED. Sends a note on when the LED is enabled, or note of if it
        is disabled.
        """
        channel = self.__led_map[led]['channel']
        note = self.__led_map[led]['note']
        if on:
            channel.send(rtmidi.MidiMessage.noteOn(1, note, 127))
        else:
            channel.send(rtmidi.MidiMessage.noteOff(1, note))
    
    def send_ctrl(self, ctrl, value):
        """
        Sends a controller value.
        """
        channel = self.__ctrl_map[ctrl]['channel']
        cc = self.__ctrl_map[ctrl]['cc']
        channel.send(rtmidi.MidiMessage.controllerEvent(1, cc, value))
    

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
        super(TranslatorFx, self).__init__(self)
        
        self.controller = core.Core.instance().get_channel_by_name(options['controller'])
        self.host = core.Core.instance().get_channel_by_name(options['host'])
        
        self.add_key('main', self.__key_main, self.controller, int(options['note_key1']))
        self.add_key('fx1', self.__key_fx1, self.controller, int(options['note_key2']))
        self.add_key('fx2', self.__key_fx2, self.controller, int(options['note_key3']))
        
        self.add_ctrl('master', self.host, int(options['cc_master']))
        self.add_ctrl('send1', self.host, int(options['cc_send1']))
        self.add_ctrl('send2', self.host, int(options['cc_send2']))
        
        self.__set_state(self.STATE_NORMAL)
        
    def __key_main(self, key):
        if self.__state == self.STATE_NORMAL:
            self.__set_state(self.STATE_MUTE)
        else:
            self.__set_state(self.STATE_NORMAL)

    def __key_fx1(self, key):
        self.__set_state(self.STATE_FX1)
        
    def __key_fx2(self, key):
        self.__set_state(self.STATE_FX2)
        
    def __set_state(self, state):
        self.__state = state
        
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
        self.send_ctrl('master', master)
        self.send_ctrl('send1', send1)
        self.send_ctrl('send2', send2)


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
        super(TranslatorLooper, self).__init__(self)

        self.controller = core.Core.instance().get_channel_by_name(options['controller'])
        self.host = core.Core.instance().get_channel_by_name(options['host'])
        
        self.add_key('key1', self.__key1, self.controller, int(options['note_key1']))
        self.add_key('key2', self.__key2, self.controller, int(options['note_key2']))
        self.add_key('key3', self.__key3, self.controller, int(options['note_key3']))
        self.add_key('key4', self.__key4, self.controller, int(options['note_key4']))
        self.add_key('key5', self.__key5, self.controller, int(options['note_key5']))
        
        self.add_led('led1', self.controller, int(options['note_led1']))
        self.add_led('led2', self.controller, int(options['note_led2']))
        self.add_led('led3', self.controller, int(options['note_led3']))
        self.add_led('led4', self.controller, int(options['note_led4']))
        
        self.add_cmd('focus', self.host, int(options['note_focus']))
        self.add_cmd('rec_add', self.host, int(options['note_rec_add']))
        self.add_cmd('play', self.host, int(options['note_play']))
        self.add_cmd('stop', self.host, int(options['note_stop']))
        self.add_cmd('clear', self.host, int(options['note_clear']))
        self.add_cmd('half', self.host, int(options['note_half']))
        self.add_cmd('double', self.host, int(options['note_double']))
        self.add_cmd('undo_redo', self.host, int(options['note_undo_redo']))
        
        self.__set_state(self.STATE_CLEAR)

    def __key1(self, key):
        self.send_cmd('focus')
        if self.__state == self.STATE_CLEAR:
            # Start recording and switch to PLAY state
            self.send_cmd('rec_add')
            self.set_led('led2', True)
            self.__set_state(self.STATE_PLAY)
        elif self.__state == self.STATE_PLAY:
            # Start overdub recording and switch to OVERDUB state
            self.send_cmd('rec_add')
            self.set_led('led1', True)
            self.__set_state(self.STATE_OVERDUB)
        elif self.__state == self.STATE_OVERDUB:
            # Stop overdub recording and switch to PLAY state
            self.send_cmd('play')
            self.set_led('led1', False)
            self.__set_state(self.STATE_PLAY)
        elif self.__state == self.STATE_IDLE:
            # Start playback and switch to PLAY state
            self.send_cmd('play')
            self.__set_state(self.STATE_PLAY)

    def __key2(self, key):
        self.send_cmd('focus')
        if self.__state == self.STATE_CLEAR:
            # Clear recording
            self.send_cmd('clear')
            self.set_led('led1', False)
            self.set_led('led2', False)
        elif self.__state == self.STATE_PLAY:
            # Stop playback and switch to IDLE state
            self.send_cmd('stop')
            self.__set_state(self.STATE_IDLE)
        elif self.__state == self.STATE_OVERDUB:
            # Stop overdub recording and switch to IDLE state
            self.send_cmd('stop')
            self.set_led('led1', False)
            self.__set_state(self.STATE_IDLE)
        elif self.__state == self.STATE_IDLE:
            # Clear recording and switch to CLEAR state
            self.send_cmd('clear')
            self.set_led('led1', False)
            self.set_led('led2', False)
            self.__set_state(self.STATE_CLEAR)

    def __key3(self, key):
        self.send_cmd('focus')
        self.send_cmd('half')

    def __key4(self, key):
        self.send_cmd('focus')
        self.send_cmd('double')
        
    def __key5(self, key):
        self.send_cmd('focus')
        self.send_cmd('undo_redo')
        
    def __set_state(self, state):
        self.__state = state
        print "Switching state to: %s" % (self.state_names[self.__state])
        
TranslatorFactory.register(TranslatorLooper)



class TranslatorSource(Translator):
    
    def __init__(self, options):
        super(TranslatorSource, self).__init__(self)
        
        self.controller = core.Core.instance().get_channel_by_name(options['controller'])
        self.host = core.Core.instance().get_channel_by_name(options['host'])
        
        self.add_key('key1', self.__key1, self.controller, int(options['note_key1']))
        self.add_key('key2', self.__key2, self.controller, int(options['note_key2']))
        self.add_key('key3', self.__key3, self.controller, int(options['note_key3']))
        self.add_key('key4', self.__key4, self.controller, int(options['note_key4']))

        self.add_ctrl('channel1', self.host, int(options['cc_channel1']))
        self.add_ctrl('channel2', self.host, int(options['cc_channel2']))
        self.add_ctrl('channel3', self.host, int(options['cc_channel3']))
        self.add_ctrl('channel4', self.host, int(options['cc_channel4']))
        self.add_ctrl('selector', self.host, int(options['cc_selector']))

        self.add_cmd('focus', self.host, int(options['note_focus']))
        
        self.__set_source(0)
        
    def __key1(self, key):
        self.__set_source(0)
    
    def __key2(self, key):
        self.__set_source(1)
    
    def __key3(self, key):
        self.__set_source(2)
        
    def __key4(self, key):
        self.__set_source(3)
        
    def __set_source(self, source):
        self.__source = source
        index = 0
        for channel in ['channel1', 'channel2', 'channel3', 'channel4']:
            if index == self.__source:
                self.send_ctrl(channel, 127)
            else:
                self.send_ctrl(channel, 0)
            index += 1
        self.send_ctrl('selector', self.__source * (127.0 / 3))
        self.send_cmd('focus')


TranslatorFactory.register(TranslatorSource)



class TranslatorRepeat(Translator):
    
    MIN_VALUE = 0
    MAX_VALUE = 10
    
    def __init__(self, options):
        super(TranslatorRepeat, self).__init__(self)

        self.controller = core.Core.instance().get_channel_by_name(options['controller'])
        self.host = core.Core.instance().get_channel_by_name(options['host'])
        
        self.add_key('key1', self.__key1, self.controller, int(options['note_key1']))
        self.add_key('key2', self.__key2, self.controller, int(options['note_key2']))
        self.add_key('key3', self.__key3, self.controller, int(options['note_key3']))
        self.add_key('key4', self.__key4, self.controller, int(options['note_key4']))
        self.add_key('key5', self.__key5, self.controller, int(options['note_key5']))
        self.add_key('key6', self.__key6, self.controller, int(options['note_key6']))

        self.add_led('led1', self.controller, int(options['note_led1']))
        self.add_led('led2', self.controller, int(options['note_led2']))
        self.add_led('led3', self.controller, int(options['note_led3']))
        self.add_led('led4', self.controller, int(options['note_led4']))
        
        self.__set_value(self.MIN_VALUE)
        
    def __key1(self, key):
        self.__set_value(0)
    
    def __key2(self, key):
        self.__set_value(1)
    
    def __key3(self, key):
        self.__set_value(2)
        
    def __key4(self, key):
        self.__set_value(3)
        
    def __key5(self, key):
        self.__set_value(self.__value - 1)
        
    def __key6(self, key):
        self.__set_value(self.__value + 1)
        
    def __set_value(self, value):
        if value < self.MIN_VALUE or value > self.MAX_VALUE:
            return
        self.__value = value

        index = self.MIN_VALUE
        for led in ['led1', 'led2', 'led3', 'led4']:
            if index == self.__value:
                self.set_led(led, True)
            else:
                self.set_led(led, False)
            index += 1


TranslatorFactory.register(TranslatorRepeat)
