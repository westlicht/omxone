
import time

from log import Logger
from midi import MidiMessage
from translator.base import Translator
from translator.factory import TranslatorFactory

class TranslatorRowSelect(Translator):
    
    def __init__(self, core, options):
        super(TranslatorRowSelect, self).__init__(core, options)

        self.controller = self.add_channel(options['controller'])
        self.host = self.add_channel(options['host'])
        
        self.__count = int(options['count'])
        key_base = int(options['key_base'])
        self.__note_base = int(options['note_base'])
        
        for i in range(0, self.__count):
            self.add_key(i, self.__key_handler, self.controller, key_base + i)
            
        for i in range(0, self.__count):
            self.add_led(i, self.controller, key_base + i)

        self.__index = -1
        self.__select(0)
        
    def __key_handler(self, key):
        print("key %d" % (key))
        self.__select(key)
    
    def __select(self, index):
        if (index == self.__index):
            return
        
        Logger.debug("Switching to %d" % (index))
        
        for i in range(0, self.__count):
            self.set_led_launchpad(i, ['off', 'green'][index == i])

        self.host.send(MidiMessage.note_on(1, self.__note_base + index, 127))
        time.sleep(0.1)
        self.host.send(MidiMessage.note_off(1, self.__note_base + index))
        
        self.__index = index


TranslatorFactory.register(TranslatorRowSelect)
