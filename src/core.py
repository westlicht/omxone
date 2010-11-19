
import rtmidi

import ConfigParser
import time
import sys

from midi import MidiEngine
from translator.factory import TranslatorFactory
from channel import Channel
from log import Logger

class Core(object):
    
    __instance = None
    
    @classmethod
    def instance(cls):
        if not cls.__instance:
            cls.__instance = Core()
        return cls.__instance
    
    def __init__(self):
        self.config = None
        self.channels = {}
        self.translators = []
            

    def run(self, options):
        """
        Runs the application. 'options' contains the CLI options dictionary.
        """
        
        # Load configuration
        self.config = ConfigParser.RawConfigParser()
        self.config.read(options.config)

        MidiEngine.initialize()
        
        Logger.debug("Command line options: %s" % (options))

        self.setup()
        
        if options.list_devices:
            self.list_devies()
        elif options.interactive:
            self.interactive_mode()
        else:
            self.loop()
            
    def setup(self):

        # Create channels
        for section in self.config.sections():
            if section.find('Channel_') == 0:
                name = self.config.get(section, 'name')
                input = self.config.get(section, 'input')
                output = self.config.get(section, 'output')
                channel = self.config.getint(section, 'channel')
                self.channels[name] = Channel(name, input, output, channel)
                
        # Create translators
        for section in self.config.sections():
            if section.find('Translator') == 0:
                values = section.split('_')
                name = values[0]
                options = {}
                for key, value in self.config.items(section):
                    options[key] = value
                translator = TranslatorFactory.create(self, name, options)
                if translator:
                    self.translators.append(translator)
                    
        # Open channels
        for channel in self.channels.values():
            channel.receive = self.__receive
            channel.open()
        
    def loop(self):
        while True:
            time.sleep(1)
            
    def add_translator(self, translator):
        self.translators.append(translator)
        
    def __receive(self, channel, msg):
        for translator in self.translators:
            translator.process(channel, msg)
            
    def get_channel_by_name(self, name):
        return self.channels[name]
        
    def list_devies(self):
        """
        Lists the name of MIDI input and output ports.
        """
        
        print "\nInput ports:"
        for input in MidiEngine.inputs:
            print " - %s" % (input.name)
            
        print "\nOutput ports:"
        for output in MidiEngine.outputs:
            print " - %s" % (output.name)


    def interactive_mode(self):
        
        terminate = False
        
        print "Usage:"
        print "[channel] [event] [params]"
        print "Examples:"
        print "xone cc 10"
        print "xone note 10"
        print
        
        while not terminate:
            line = sys.stdin.readline()
            values = line.split(' ')
            if len(values) < 3:
                continue
            channel = self.get_channel_by_name(values[0])
            if not channel:
                continue
            cmd = values[1]
            value = int(values[2])
            print channel, cmd, value
            if cmd == 'cc':
                channel.send(rtmidi.MidiMessage.controllerEvent(1, value, 100))
                channel.send(rtmidi.MidiMessage.controllerEvent(1, value, 101))
                channel.send(rtmidi.MidiMessage.controllerEvent(1, value, 100))
            elif cmd == 'note':
                channel.send(rtmidi.MidiMessage.noteOn(1, value, 100))
                channel.send(rtmidi.MidiMessage.noteOff(1, value))
