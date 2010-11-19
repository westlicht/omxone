
from log import Logger
from translator.base import Translator
from translator.factory import TranslatorFactory

class TranslatorFXSelect(Translator):
    
    def __init__(self, core, options):
        super(TranslatorFXSelect, self).__init__(core, options)

        self.controller = self.add_channel(options['controller'])
        self.host = self.add_channel(options['host'])
        
        self.add_key('key1', self.__key_fx1, self.controller, int(options['key_fx1']))
        self.add_key('key2', self.__key_fx2, self.controller, int(options['key_fx2']))
        self.add_key('key3', self.__key_fx3, self.controller, int(options['key_fx3']))
        self.add_key('key4', self.__key_fx4, self.controller, int(options['key_fx4']))

        self.add_led('led1', self.controller, int(options['note_led1']))
        self.add_led('led2', self.controller, int(options['note_led2']))
        self.add_led('led3', self.controller, int(options['note_led3']))
        self.add_led('led4', self.controller, int(options['note_led4']))
        
        self.add_ctrl('fx1', self.host, int(options['cc_fx1']))
        self.add_ctrl('fx2', self.host, int(options['cc_fx2']))
        self.add_ctrl('fx3', self.host, int(options['cc_fx3']))
        self.add_ctrl('fx4', self.host, int(options['cc_fx4']))
        
        self.send_ctrl('fx1', 0)
        self.send_ctrl('fx2', 0)
        self.send_ctrl('fx3', 0)
        self.send_ctrl('fx4', 0)
        
        self.__state = [False, False, False, False]
        
    def __key_fx1(self, key):
        self.__switch(0)
    
    def __key_fx2(self, key):
        self.__switch(1)
    
    def __key_fx3(self, key):
        self.__switch(2)
        
    def __key_fx4(self, key):
        self.__switch(3)
        
    def __switch(self, fx):
        self.__state[fx] = not self.__state[fx]
        Logger.debug("Switching state of fx%d to %d" % (fx, self.__state[fx]))
        
        if self.__state[fx]:
            value = 127
        else:
            value = 0
            
        self.send_ctrl(['fx1', 'fx2', 'fx3', 'fx4'][fx], value)
        self.set_led(['led1', 'led2', 'led3', 'led4'][fx], self.__state[fx])


TranslatorFactory.register(TranslatorFXSelect)
