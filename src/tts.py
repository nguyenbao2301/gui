from gtts import gTTS
import os
from src.utils import PlaySound

from configparser import ConfigParser
config = ConfigParser()
config.read('config.ini')
class TTS():

    def __init__(self):
        self.volume = config.get('main','tts_volume')

    def speak(self,text):
        tts = gTTS(text,lang = 'vi')
        print(text)
        path = os.path.join(config.get('main','temp_dir'),'tts_temp.mp3')
        tts.save(path)
        PlaySound(path,self.volume)
