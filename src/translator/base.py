
import rtmidi

import core
from log import Logger

class Translator(object):
    
    def __init__(self, options):
        
        self.__key_map = {}
        self.__cmd_map = {}
        self.__led_map = {}
        self.__ctrl_map = {}
            
    def process(self, channel, msg):
        """
        Called for incoming MIDI messages. Calls the registered key handlers.
        """
        if msg.isNoteOn():
            try:
                info = self.__key_map[channel][msg.getNoteNumber()]
                info['handler'](info['key'])
            except KeyError:
                pass
    
    def send(self, channel, msg):
        channel.send(msg)
        
    def add_key(self, key, handler, channel, note):
        """
        Adds a key handler to the translator. The key handler is triggered
        when receiving the specified note on the given channel.
        """
        try:
            channel_map = self.__key_map[channel]
        except KeyError:
            channel_map = {}
            self.__key_map[channel] = channel_map
        channel_map[note] = { 'key': key, 'handler': handler }
        
    def add_cmd(self, cmd, channel, note):
        """
        Adds a command to the translator. When sending the command using
        send_cmd() a note on/off is sent using the specified note on the
        given channel.
        """
        self.__cmd_map[cmd] = { 'channel': channel, 'note': note }
        pass
    
    def add_led(self, led, channel, note):
        """
        Adds a LED to the translator. When setting the LED using set_led()
        a note on/off is sent using the specified note on the given channel.
        """
        self.__led_map[led] = { 'channel': channel, 'note': note }
    
    def add_ctrl(self, ctrl, channel, cc):
        """
        Adds a controller to the translator. When sending a controller value
        using send_ctrl() a CC is sent using the specified CC number on the
        given channel.
        """
        self.__ctrl_map[ctrl] = { 'channel': channel, 'cc': cc }
    
    def send_cmd(self, cmd):
        """
        Sends a command. This will send a note on followed by note off event.
        """
        channel = self.__cmd_map[cmd]['channel']
        note = self.__cmd_map[cmd]['note']
        channel.send(rtmidi.MidiMessage.noteOn(1, note, 127))
        channel.send(rtmidi.MidiMessage.noteOff(1, note))
    
    def set_led(self, led, on):
        """
        Sets a LED. Sends a note on when the LED is enabled, or note of if it
        is disabled.
        """
        channel = self.__led_map[led]['channel']
        note = self.__led_map[led]['note']
        if on:
            channel.send(rtmidi.MidiMessage.noteOn(1, note, 127))
        else:
            channel.send(rtmidi.MidiMessage.noteOff(1, note))
    
    def send_ctrl(self, ctrl, value):
        """
        Sends a controller value.
        """
        channel = self.__ctrl_map[ctrl]['channel']
        cc = self.__ctrl_map[ctrl]['cc']
        channel.send(rtmidi.MidiMessage.controllerEvent(1, cc, value))
