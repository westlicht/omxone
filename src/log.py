

class Logger(object):
    
    OFF = 0
    INFO = 1
    DEBUG = 2
    
    level = DEBUG
    
    @classmethod
    def info(cls, text):
        cls.log(cls.INFO, text)
    
    @classmethod
    def debug(cls, text):
        cls.log(cls.DEBUG, text)
        
    @classmethod
    def log(cls, level, text):
        if level <= cls.level:
            print(text)
        