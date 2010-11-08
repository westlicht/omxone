
import traceback
import binascii
import rtmidi


def dump_msg(msg):
    raw = binascii.hexlify(msg.getRawData())
    channel = msg.getChannel()    
    if msg.isNoteOn():
        print raw, channel, 'ON: ', msg.getNoteNumber(), msg.getVelocity()
    elif msg.isNoteOff():
        print raw, channel, 'OFF:', msg.getNoteNumber()
    elif msg.isController():
        print raw, channel, 'CONTROLLER', msg.getControllerNumber(), msg.getControllerValue()


class MidiEngine(object):
    
    inputs = []
    outputs = []
    
    @classmethod
    def initialize(cls):
        cls.inputs = []
        cls.outputs = []
    
        midi_in = rtmidi.RtMidiIn()
        for i in range(midi_in.getPortCount()):
            cls.inputs.append(MidiInput(i))

        midi_out = rtmidi.RtMidiOut()
        for i in range(midi_out.getPortCount()):
            cls.outputs.append(MidiOutput(i))
    
    @classmethod
    def get_input_by_name(cls, name):
        for input in cls.inputs:
            if input.name == name:
                return input
        return None
    
    @classmethod
    def get_output_by_name(cls, name):
        for output in cls.outputs:
            if output.name == name:
                return output
        return None
        
    @classmethod
    def dump_msg(cls, msg):
        raw = binascii.hexlify(msg.getRawData())
        channel = msg.getChannel()    
        if msg.isNoteOn():
            return raw, channel, 'ON: ', msg.getNoteNumber(), msg.getVelocity()
        elif msg.isNoteOff():
            return raw, channel, 'OFF:', msg.getNoteNumber()
        elif msg.isController():
            return raw, channel, 'CONTROLLER', msg.getControllerNumber(), msg.getControllerValue()


class MidiInput(object):
    
    def __init__(self, port):
        self.__port = port
        self.__midi = rtmidi.RtMidiIn()
        self.name = self.__midi.getPortName(self.__port)
        self.receive = None
        
    def open(self):
        self.__midi.openPort(self.__port)
        self.__midi.setCallback(self.__receive)
        
    def __receive(self, msg):
        if self.receive:
            try:
                self.receive(self, msg)
            except Exception as e:
                print e

  
    
class MidiOutput(object):
    
    def __init__(self, port):
        self.__port = port
        self.__midi = rtmidi.RtMidiOut()
        self.name = self.__midi.getPortName(self.__port)
        
    def open(self):
        self.__midi.openPort(self.__port)

    def send(self, msg):
        try:
            self.__midi.sendMessage(msg)
        except Exception as e:
            print e

