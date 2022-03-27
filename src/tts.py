import pyttsx3

class TTS():

    def __init__(self):
        self.engine = pyttsx3.init()
         # engine.setProperty('rate',135)
        voices = self.engine.getProperty('voices') 
        self.engine.setProperty('voice', voices[1].id) 
        self.engine.setProperty('volume', 0.5)

    def speak(self,text):
        engine = self.engine
        print(text)
        engine.say(text)
        engine.runAndWait()