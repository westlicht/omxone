
from translator.base import Translator
from translator.factory import TranslatorFactory

class TranslatorSource(Translator):
    
    def __init__(self, core, options):
        super(TranslatorSource, self).__init__(core, options)
        
        self.controller = self.add_channel(options['controller'])
        self.host = self.add_channel(options['host'])
        
        self.add_key('key1', self.__key_channel1, self.controller, int(options['key_channel1']))
        self.add_key('key2', self.__key_channel2, self.controller, int(options['key_channel2']))
        self.add_key('key3', self.__key_channel3, self.controller, int(options['key_channel3']))
        self.add_key('key4', self.__key_channel4, self.controller, int(options['key_channel4']))

        self.add_ctrl('channel1', self.host, int(options['cc_channel1']))
        self.add_ctrl('channel2', self.host, int(options['cc_channel2']))
        self.add_ctrl('channel3', self.host, int(options['cc_channel3']))
        self.add_ctrl('channel4', self.host, int(options['cc_channel4']))
        self.add_ctrl('selector', self.host, int(options['cc_selector']))

        self.add_cmd('focus', self.host, int(options['note_focus']))
        
        self.__set_source(0)
        
    def __key_channel1(self, key):
        self.__set_source(0)
    
    def __key_channel2(self, key):
        self.__set_source(1)
    
    def __key_channel3(self, key):
        self.__set_source(2)
        
    def __key_channel4(self, key):
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
