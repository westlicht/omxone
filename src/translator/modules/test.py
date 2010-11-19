
from translator.base import Translator
from translator.factory import TranslatorFactory

class TranslatorTest(Translator):
    
    def __init__(self, core, options):
        super(TranslatorTest, self).__init__(core, options)

        self.controller = self.add_channel(options['controller'])
        self.host = self.add_channel(options['host'])
        
TranslatorFactory.register(TranslatorTest)
