

class Logger(object):
    
    OFF = 0
    INFO = 1
    DEBUG = 2
    
    level = OFF
    
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
        
    @classmethod
    def set_log_level(cls, level):
        cls.level = level
    