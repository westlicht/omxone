
from midi import MidiEngine
from log import Logger

class Channel(object):
    
    def __init__(self, name, input, output, channel):
        Logger.debug("[%s] Initializing channel: input='%s', output='%s, channel=%d" % (name, input, output, channel))
        self.name = name
        self.input = MidiEngine.get_input_by_name(input)
        self.output = MidiEngine.get_output_by_name(output)
        self.channel = channel
        self.receive = None
        
        if self.input:
            self.input.receive = self.__receive
            
    def open(self):
        if self.input:
            self.input.open()
        if self.output:
            self.output.open()
        
    def send(self, msg):
        # Override MIDI channel
        msg.setChannel(self.channel)
        Logger.debug("[%s] Sending message: %s" % (self.name, MidiEngine.dump_msg(msg)))
        if self.output:
            self.output.send(msg)
        
        
    def __receive(self, input, msg):
        # Filter message if it does not belong to the configured MIDI channel
        if msg.getChannel() != self.channel:
            return
        Logger.debug("[%s] Received message: %s" % (self.name, MidiEngine.dump_msg(msg)))
        # Dispatch received message
        if self.receive:
            self.receive(self, msg)
            
    