
import time

from log import Logger
from translator.base import Translator
from translator.factory import TranslatorFactory

class TranslatorMIDISource(Translator):
    
    def __init__(self, core, options):
        super(TranslatorMIDISource, self).__init__(core, options)
        
        self.controller = self.add_channel(options['controller'])
        self.host = self.add_channel(options['host'])
        
        self.add_knob('source1', self.__knob_source, self.controller, int(options['knob_source1']))
        self.add_knob('source2', self.__knob_source, self.controller, int(options['knob_source2']))
        self.add_knob('source3', self.__knob_source, self.controller, int(options['knob_source3']))
        self.add_knob('source4', self.__knob_source, self.controller, int(options['knob_source4']))
        self.add_knob('source5', self.__knob_source, self.controller, int(options['knob_source5']))
        self.add_knob('source6', self.__knob_source, self.controller, int(options['knob_source6']))
        self.add_knob('source7', self.__knob_source, self.controller, int(options['knob_source7']))
        
        self.add_ctrl('source1', self.host, int(options['cc_source1']))
        self.add_ctrl('source2', self.host, int(options['cc_source2']))
        self.add_ctrl('source3', self.host, int(options['cc_source3']))
        self.add_ctrl('source4', self.host, int(options['cc_source4']))
        self.add_ctrl('source5', self.host, int(options['cc_source5']))
        self.add_ctrl('source6', self.host, int(options['cc_source6']))
        self.add_ctrl('source7', self.host, int(options['cc_source7']))
        
    def __knob_source(self, knob, value):
        
        self.send_ctrl('source1', 0)
        self.send_ctrl('source2', 0)
        self.send_ctrl('source3', 0)
        self.send_ctrl('source4', 0)
        self.send_ctrl('source5', 0)
        self.send_ctrl('source6', 0)
        self.send_ctrl('source7', 0)
        self.send_ctrl(knob, 127)



TranslatorFactory.register(TranslatorMIDISource)
