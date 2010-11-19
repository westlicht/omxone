
from log import Logger
from translator.base import Translator
from translator.factory import TranslatorFactory

class TranslatorLooper(Translator):
    
    STATE_CLEAR = 0
    STATE_PLAY = 1
    STATE_OVERDUB = 2
    STATE_IDLE = 3
    
    state_names = {
        STATE_CLEAR     : 'clear',
        STATE_PLAY      : 'play',
        STATE_OVERDUB   : 'overdub',
        STATE_IDLE      : 'idle',
    }
    
    def __init__(self, core, options):
        super(TranslatorLooper, self).__init__(core, options)

        self.controller = self.add_channel(options['controller'])
        self.host = self.add_channel(options['host'])
        
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

        self.set_led('led1', False)
        self.set_led('led2', False)
        self.set_led('led3', False)
        self.set_led('led4', False)
        self.send_cmd('stop')
        self.send_cmd('clear')

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
        Logger.debug("Switching state to: %s" % (self.state_names[self.__state]))
        
TranslatorFactory.register(TranslatorLooper)
