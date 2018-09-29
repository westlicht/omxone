
import rtmidi

from log import Logger
from midi import MidiMessage

class Translator(object):
    
    def __init__(self, core, options):
        
        self.__core = core
        self.__key_map = {}
        self.__knob_map = {}
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
        if msg.isController():
            try:
                info = self.__knob_map[channel][msg.getControllerNumber()]
                info['handler'](info['knob'], msg.getControllerValue())
            except KeyError:
                pass
    
    def send(self, channel, msg):
        channel.send(msg)
        
    def add_channel(self, name):
        """
        Adds a new channel to the translator.
        """
        return self.__core.get_channel_by_name(name)
        
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
        
    def add_knob(self, knob, handler, channel, cc):
        """
        Adds a knob handler to the translator. The knob handler is called
        when receiving the specified controller change on the given channel.
        """
        try:
            channel_map = self.__knob_map[channel]
        except KeyError:
            channel_map = {}
            self.__knob_map[channel] = channel_map
        channel_map[cc] = { 'knob': knob, 'handler': handler }
        
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
    
    def send_cmd(self, cmd, velocity=127):
        """
        Sends a command. This will send a note on followed by note off event.
        """
        channel = self.__cmd_map[cmd]['channel']
        note = self.__cmd_map[cmd]['note']
        channel.send(MidiMessage.note_on(1, note, velocity))
        channel.send(MidiMessage.note_off(1, note))

    def set_led(self, led, on):
        """
        Sets a LED. Sends a note on when the LED is enabled, or note of if it
        is disabled.
        """
        channel = self.__led_map[led]['channel']
        note = self.__led_map[led]['note']
        if on:
            channel.send(MidiMessage.note_on(1, note, 127))
        else:
            channel.send(MidiMessage.note_off(1, note))
    
    def set_led_launchpad(self, led, color):
        """
        Sets a LED. Sends a note on when the LED is enabled, or note of if it
        is disabled.
        """
        channel = self.__led_map[led]['channel']
        note = self.__led_map[led]['note']
        if color == 'off':
            channel.send(MidiMessage.note_on(1, note, 0x04))
        elif color == 'red':
            channel.send(MidiMessage.note_on(1, note, 0x07))
        elif color == 'green':
            channel.send(MidiMessage.note_on(1, note, 0x34))
        elif color == 'yellow':
            channel.send(MidiMessage.note_on(1, note, 0x37))
    
    def send_ctrl(self, ctrl, value):
        """
        Sends a controller value.
        """
        channel = self.__ctrl_map[ctrl]['channel']
        cc = self.__ctrl_map[ctrl]['cc']
        channel.send(MidiMessage.controller_event(1, cc, int(value)))
