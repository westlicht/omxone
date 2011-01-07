
import time

from log import Logger
from translator.base import Translator
from translator.factory import TranslatorFactory

class TranslatorDoubleFilter(Translator):
    
    RANGE = 127
    DEAD = 0.05
    
    def __init__(self, core, options):
        super(TranslatorDoubleFilter, self).__init__(core, options)
        
        self.controller = self.add_channel(options['controller'])
        self.host = self.add_channel(options['host'])
        
        self.add_knob('cutoff', self.__knob_cutoff, self.controller, int(options['knob_cutoff']))
        
        self.add_ctrl('cutoff_lp', self.host, int(options['cc_cutoff_lp']))
        self.add_ctrl('cutoff_hp', self.host, int(options['cc_cutoff_hp']))
        
    def __knob_cutoff(self, knob, value):
        
        cutoff = float(value) / self.RANGE
        lp = 1.0
        hp = 0.0
        if cutoff < 0.5 - self.DEAD:
            lp = cutoff / (0.5 - self.DEAD)
        elif cutoff > 0.5 + self.DEAD:
            hp = (cutoff - (0.5 + self.DEAD)) / (0.5 - self.DEAD)
            
        self.send_ctrl('cutoff_lp', round(lp * self.RANGE))
        self.send_ctrl('cutoff_hp', round(hp * self.RANGE))
        



TranslatorFactory.register(TranslatorDoubleFilter)
