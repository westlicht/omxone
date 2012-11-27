
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
        
        self.add_key('key_rec', self.__key_rec, self.controller, int(options['key_rec']))
        self.add_key('key_stop', self.__key_stop, self.controller, int(options['key_stop']))
        self.add_key('key_rev', self.__key_rev, self.controller, int(options['key_rev']))
        self.add_key('key_half', self.__key_half, self.controller, int(options['key_half']))
        self.add_key('key_double', self.__key_double, self.controller, int(options['key_double']))
        self.add_key('key_undo', self.__key_undo, self.controller, int(options['key_undo']))
        
        self.add_led('led_state', self.controller, int(options['led_state']))
        self.add_led('led_data', self.controller, int(options['led_data']))
        self.add_led('led_rev', self.controller, int(options['led_rev']))
        self.add_led('led_half', self.controller, int(options['led_half']))
        self.add_led('led_double', self.controller, int(options['led_double']))
        
        self.add_cmd('focus', self.host, int(options['note_focus']))
        self.add_cmd('rec_add', self.host, int(options['note_rec_add']))
        self.add_cmd('play', self.host, int(options['note_play']))
        self.add_cmd('stop', self.host, int(options['note_stop']))
        self.add_cmd('clear', self.host, int(options['note_clear']))
        self.add_cmd('rev', self.host, int(options['note_rev']))
        self.add_cmd('half', self.host, int(options['note_half']))
        self.add_cmd('double', self.host, int(options['note_double']))
        self.add_cmd('undo_redo', self.host, int(options['note_undo_redo']))
        
        self.__rev = False
        self.__set_state(self.STATE_CLEAR)

        self.set_led_launchpad('led_state', 'red')
        self.set_led_launchpad('led_data', 'off')
        self.set_led_launchpad('led_rev', 'off')
        self.set_led_launchpad('led_half', 'yellow')
        self.set_led_launchpad('led_double', 'yellow')
        self.send_cmd('stop')
        self.send_cmd('clear')

    def __key_rec(self, key):
        self.send_cmd('focus')
        if self.__state == self.STATE_CLEAR:
            # Start recording and switch to PLAY state
            self.send_cmd('rec_add')
            self.set_led_launchpad('led_state', 'red')
            self.set_led_launchpad('led_data', 'yellow')
            self.__set_state(self.STATE_PLAY)
        elif self.__state == self.STATE_PLAY:
            # Start overdub recording and switch to OVERDUB state
            self.send_cmd('rec_add')
            self.set_led_launchpad('led_state', 'yellow')
            self.__set_state(self.STATE_OVERDUB)
        elif self.__state == self.STATE_OVERDUB:
            # Stop overdub recording and switch to PLAY state
            self.send_cmd('play')
            self.set_led_launchpad('led_state', 'green')
            self.__set_state(self.STATE_PLAY)
        elif self.__state == self.STATE_IDLE:
            # Start playback and switch to PLAY state
            self.send_cmd('play')
            self.set_led_launchpad('led_state', 'green')
            self.__set_state(self.STATE_PLAY)

    def __key_stop(self, key):
        self.send_cmd('focus')
        if self.__state == self.STATE_CLEAR:
            # Clear recording
            self.send_cmd('clear')
            self.set_led_launchpad('led_state', 'red')
            self.set_led_launchpad('led_data', 'off')
        elif self.__state == self.STATE_PLAY:
            # Stop playback and switch to IDLE state
            self.send_cmd('stop')
            self.set_led_launchpad('led_state', 'off')
            self.__set_state(self.STATE_IDLE)
        elif self.__state == self.STATE_OVERDUB:
            # Stop overdub recording and switch to IDLE state
            self.send_cmd('stop')
            self.set_led_launchpad('led_state', 'off')
            self.__set_state(self.STATE_IDLE)
        elif self.__state == self.STATE_IDLE:
            # Clear recording and switch to CLEAR state
            self.send_cmd('clear')
            self.set_led_launchpad('led_state', 'red')
            self.set_led_launchpad('led_data', 'off')
            self.__set_state(self.STATE_CLEAR)

    def __key_rev(self, key):
        self.send_cmd('rev')
        self.__rev = not self.__rev
        self.set_led_launchpad('led_rev', ['off','yellow'][self.__rev])

    def __key_half(self, key):
        self.send_cmd('focus')
        self.send_cmd('half')

    def __key_double(self, key):
        self.send_cmd('focus')
        self.send_cmd('double')
        
    def __key_undo(self, key):
        self.send_cmd('focus')
        self.send_cmd('undo_redo')
        
    def __set_state(self, state):
        self.__state = state
        Logger.debug("Switching state to: %s" % (self.state_names[self.__state]))
        
TranslatorFactory.register(TranslatorLooper)
