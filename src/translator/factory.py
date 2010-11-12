
from log import Logger

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
