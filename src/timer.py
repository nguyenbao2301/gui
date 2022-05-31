import time
import datetime
import threading 
from PIL import Image,ImageTk
import tkinter as tk
from audioplayer import AudioPlayer
from configparser import ConfigParser
config = ConfigParser()
config.read('config.ini')

class TimerThread(threading.Thread):
    def __init__(self,h,m,s,target):
        threading.Thread.__init__(self)
        self.total = 0
        self.target = target
        self.total = 3600*h + 60*m + s
        self.daemon = True
        self.audio = None
        self.flag = True
        print(h,m,s,self.total)
        

        img_path = "./img/alarm_overlay.png"
        w,h = int(config.get("main","width")),int(config.get("main","height"))
        img= (Image.open(img_path))
        img= img.resize((w,h),resample=Image.LANCZOS)
        self.img= ImageTk.PhotoImage(img)
        
    def run(self):
        try:
                
                while self.total>0:
                    timer = datetime.timedelta(seconds = self.total)
                    print(timer,end='\r')
                    time.sleep(1)
                    self.total -= 1
                _audio = config.get('main','timer_dir')
                _volume = int(config.get('main','timer_volume'))
                try:
                    if self.audio == None:
                        self.audio = AudioPlayer(_audio)
                        self.audio.volume = _volume
                        self.audio.play(loop=True)
                except Exception:
                    print("audio alarm error")
                self.display(self.target)
                while(self.flag):
                    continue
        finally:
            if self.audio != None:
                self.audio.stop()
            print('ended')

    def display(self, target):
        print("alarm triggered")
        
        alarmFrame = tk.Label(target,image=self.img,text = "\n\nDouble click to close.",fg="blue",bg="beige")
        alarmFrame.image = self.img
        alarmFrame.place(in_=target,x=-1,y=-1,anchor="nw")

        alarmFrame.bind('<Double-Button-1>', lambda x: self._close(alarmFrame))

    def _close(self,frame):
        self.flag = False
        frame.destroy()

