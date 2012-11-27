
import time

from log import Logger
from translator.base import Translator
from translator.factory import TranslatorFactory

class TranslatorFx(Translator):
    
    STATE_NORMAL = 0
    STATE_MUTE = 1
    STATE_FX1 = 2
    STATE_FX2 = 3
    
    SWITCH_INTERVAL = 0.02
    
    state_names = {
        STATE_NORMAL    : 'Normal',
        STATE_MUTE      : 'Mute',
        STATE_FX1       : 'FX1',
        STATE_FX2       : 'FX2',
    }
    
    def __init__(self, core, options):
        super(TranslatorFx, self).__init__(core, options)
        
        self.controller = self.add_channel(options['controller'])
        self.host = self.add_channel(options['host'])
        self.launchpad = bool(options['launchpad'])
        
        self.add_key('main', self.__key_main, self.controller, int(options['key_main']))
        self.add_key('fx1', self.__key_fx1, self.controller, int(options['key_fx1']))
        self.add_key('fx2', self.__key_fx2, self.controller, int(options['key_fx2']))
        self.add_key('reset', self.__key_reset, self.controller, int(options['key_reset']))
        
        if self.launchpad:
            self.add_led('main', self.controller, int(options['key_main']))
            self.add_led('fx1', self.controller, int(options['key_fx1']))
            self.add_led('fx2', self.controller, int(options['key_fx2']))
        
        self.add_ctrl('master', self.host, int(options['cc_master']))
        self.add_ctrl('send1', self.host, int(options['cc_send1']))
        self.add_ctrl('send2', self.host, int(options['cc_send2']))
        self.add_ctrl('selector', self.host, int(options['cc_selector']))
        
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
        
    def __key_reset(self, key):
        self.__set_state(self.STATE_NORMAL)
        
    def __set_state(self, state):
        self.__state = state
        
        Logger.debug("Switching to state %s" % (self.state_names[self.__state]))

        if self.__state == self.STATE_NORMAL:
            self.__update_levels(127, 0, 0)
            self.send_ctrl('master', 127)
            time.sleep(self.SWITCH_INTERVAL)
            self.send_ctrl('send1', 0)
            self.send_ctrl('send2', 0)
        elif self.__state == self.STATE_MUTE:
            self.__update_levels(0, 0, 0)
            self.send_ctrl('master', 0)
            self.send_ctrl('send1', 0)
            self.send_ctrl('send2', 0)
        elif self.__state == self.STATE_FX1:
            self.__update_levels(0, 127, 0)
            self.send_ctrl('send1', 127)
            time.sleep(self.SWITCH_INTERVAL)
            self.send_ctrl('master', 0)
            self.send_ctrl('send2', 0)
        elif self.__state == self.STATE_FX2:
            self.__update_levels(0, 0, 127)
            time.sleep(self.SWITCH_INTERVAL)
            self.send_ctrl('send2', 127)
            self.send_ctrl('master', 0)
            self.send_ctrl('send1', 0)
            
        self.send_ctrl('selector', (self.__state / 3.0) * 127.0)
        
        if self.launchpad:
            self.set_led_launchpad('main', ['green', 'red', 'off', 'off'][self.__state])
            self.set_led_launchpad('fx1', ['off', 'red', 'green', 'off'][self.__state])
            self.set_led_launchpad('fx2', ['off', 'red', 'off', 'green'][self.__state])
        
    def __update_levels(self, master, send1, send2):
        return
        self.send_ctrl('master', master)
        self.send_ctrl('send1', send1)
        self.send_ctrl('send2', send2)


TranslatorFactory.register(TranslatorFx)
