
from log import Logger

class TranslatorFactory(object):
    
    translators = {}
    
    @classmethod
    def register(cls, translator):
        Logger.debug("Registering translator class '%s'" % (translator.__name__))
        cls.translators[translator.__name__] = translator
    
    @classmethod
    def create(cls, core, name, options):
        Logger.debug("Creating translator class '%s' with options: %s" % (name, options))
        return cls.translators[name](core, options)

import modules
