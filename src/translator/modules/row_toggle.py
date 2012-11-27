
import time

from log import Logger
from midi import MidiMessage
from translator.base import Translator
from translator.factory import TranslatorFactory

class TranslatorRowToggle(Translator):
    
    def __init__(self, core, options):
        super(TranslatorRowToggle, self).__init__(core, options)

        self.controller = self.add_channel(options['controller'])
        self.host = self.add_channel(options['host'])
        
        self.__count = int(options['count'])
        key_base = int(options['key_base'])
        self.__note_enable_base = int(options['note_enable_base'])
        self.__cc_monitor_base = int(options['cc_monitor_base'])
        
        for i in range(0, self.__count):
            self.add_key(i, self.__key_handler, self.controller, key_base + i)
            self.add_led(i, self.controller, key_base + i)

        self.__state = [False] * self.__count

        self.__clear()
        
    def __key_handler(self, key):
        self.__state[key] = not self.__state[key]
        
        self.set_led_launchpad(key, ['off', 'green'][self.__state[key]])
        
        if self.__state[key]:
            self.host.send(MidiMessage.note_on(1, self.__note_enable_base + key, 127))
            self.host.send(MidiMessage.note_off(1, self.__note_enable_base + key))
            self.host.send(MidiMessage.controller_event(1, self.__cc_monitor_base + key, 0))
        else:
            self.host.send(MidiMessage.controller_event(1, self.__cc_monitor_base + key, 127))
        
    
    def __clear(self):
        for i in range(0, self.__count):
            self.set_led_launchpad(i, 'off')
            self.host.send(MidiMessage.controller_event(1, self.__cc_monitor_base + i, 127))


TranslatorFactory.register(TranslatorRowToggle)
