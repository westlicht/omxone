
import time

from translator.base import Translator
from translator.factory import TranslatorFactory

class TranslatorTransport(Translator):
    
    def __init__(self, core, options):
        super(TranslatorTransport, self).__init__(core, options)
        
        self.controller = self.add_channel(options['controller'])
        self.host = self.add_channel(options['host'])
        
        self.add_key('live_play', self.__live_play, self.host, int(options['live_play']))
        self.add_key('live_prev_scene', self.__live_prev_scene, self.host, int(options['live_prev_scene']))
        self.add_key('live_next_scene', self.__live_next_scene, self.host, int(options['live_next_scene']))
        self.add_key('key_play', self.__key_play, self.controller, int(options['key_play']))
        self.add_key('key_prev_scene', self.__key_prev_scene, self.controller, int(options['key_prev_scene']))
        self.add_key('key_next_scene', self.__key_next_scene, self.controller, int(options['key_next_scene']))

        self.add_cmd('play', self.host, int(options['note_play']))
        self.add_cmd('prev_scene', self.host, int(options['note_prev_scene']))
        self.add_cmd('next_scene', self.host, int(options['note_next_scene']))
        
    def __live_play(self, key):
        self.send_cmd('play')
    
    def __live_prev_scene(self, key):
        self.send_cmd('prev_scene')
    
    def __live_next_scene(self, key):
        self.send_cmd('next_scene')
    
    def __key_play(self, key):
        self.send_cmd('play')
    
    def __key_prev_scene(self, key):
        pass
		#self.send_cmd('prev_scene')
        
    def __key_next_scene(self, key):
        pass
		#self.send_cmd('next_scene')
        

TranslatorFactory.register(TranslatorTransport)
