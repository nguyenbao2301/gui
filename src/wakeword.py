import speech_recognition as sr
import pyaudio
import wave
import os

from configparser import ConfigParser
config = ConfigParser()
config.read('config.ini')

class Listener:

    def __init__(self):
        self.chunk = 1024
        self.FORMAT = pyaudio.paInt16
        self.channels = 1
        self.sample_rate = 16000

        self.p = pyaudio.PyAudio()

        self.stream = self.p.open(format=self.FORMAT,
                        channels=self.channels,
                        rate=self.sample_rate,
                        input=True,
                        output=True,
                        frames_per_buffer=self.chunk)


    def save_audio(self, frames, file_name = "wakeword_temp.wav"):
        # print('saving file to {}'.format(file_name))
        file_name = os.path.join(config.get('main', 'temp_dir'),file_name)
        wf = wave.open(file_name, "wb")
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
        wf.setframerate(self.sample_rate)
        wf.writeframes(b"".join(frames))
        wf.close()
        return file_name

def start():
    #setup 
    # create recognizer and mic instances
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    recognizer.non_speaking_duration = 0.5
    recognizer.pause_threshold = 1
    
    print("Configuring, please wait...")
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)

    return recognizer,microphone