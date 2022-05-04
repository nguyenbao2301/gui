import threading 
import ctypes
from src.services import MusicService,AlarmTimerService,WeatherService,SearchService
from src.ASRBubble import ASRBubble
from src.tts import TTS

from configparser import ConfigParser
config = ConfigParser()
config.read('config.ini')

class processThread(threading.Thread):
    def __init__(self,master,recognizer,microphone,idsf):
        threading.Thread.__init__(self)
        self.idsf = idsf
        self.microphone = microphone
        self.recognizer = recognizer
        self.master = master
    def run(self):     
        try:       
            with self.microphone as source:
                audio = self.recognizer.listen(source,phrase_time_limit = 5)
                try:
                    response = self.recognizer.recognize_google(audio,language="vi-VN")
                except Exception:
                    response = None
            
            if response != None:
                ASRBubble(self.master,response.lower())
                # time.sleep(2)
                text,intent,slots = self.idsf.predict(response.lower())
                # print(intent,text,slots)
                process(intent,text,slots,self.master)
                
                    # processor.process(response.lower())
            else:
                ASRBubble(self.master,"Xin lỗi, tôi không nghe rõ câu đó")  
                TTS().speak("Xin lỗi, tôi không nghe rõ câu đó")   
        finally:
            self.master.resetImg()        

    def get_id(self):
 
        # returns id of the respective thread
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id
  
    def raise_exception(self):
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
              ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')
def extract(text,labels):
    content = ""
    temp = ""
    arr = {}
    print(labels)
    for word,label in zip(text.split(),labels):
        if label[0] == "O":
            if content != "" and content not in arr.keys():
                arr[content] = temp[:-1]
            content = ""
            temp = ""
        elif label[0] == "B":
            if(label[2:] != content) and content != "" and content not in arr.keys():
                arr[content] = temp[:-1]
                temp = ""
            content = label[2:]
            print(content)
        if content != "":
            temp = temp + word + " "
    if content != "" and content not in arr.keys():
        arr[content] = temp[:-1]
    print(arr)
    return arr

def recognize(master,recognizer,microphone,idsf):
    with microphone as source:
            audio = recognizer.listen(source,phrase_time_limit = 5)
            try:
                response = recognizer.recognize_google(audio,language="vi-VN")
            except Exception:
                response = None
            
    if response != None:
        ASRBubble(master,response.lower())
        # time.sleep(2)
        text,intent,slots = idsf.predict(response.lower())
        # print(intent,text,slots)
        
        p = processThread(intent,text,slots,master)
        p.start()
        
            # processor.process(response.lower())
    else:
        ASRBubble(master,"Xin lỗi, tôi không nghe rõ câu đó")  
        TTS().speak("Xin lỗi, tôi không nghe rõ câu đó")   
        
def process(intent,text,slots,master):
            print(intent,text,slots)
            arr = extract(text,slots)
            
            if intent == "play_song":
                music = MusicService(master,arr,text)
                query = music.createQuery()
                link = music.searchQuery(query)
                music.play(link)
            

            elif intent == "alarm":
                ats = AlarmTimerService(master,arr)
                ats.setAlarm()
            

            elif intent == "timer":
                ats = AlarmTimerService(master,arr)
                ats.setTimer(master)
                

            elif intent == "weather":
                ws =WeatherService(master,arr)
                query = ws.createQuery()
                if query!= "": 
                    ws.searchQuery(query)
                else:
                    s = SearchService(master,arr)
                    s.search(text)    

            else:
                s = SearchService(master,arr)
                s.search(text)
            return