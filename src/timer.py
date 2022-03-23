import time
import datetime
import threading 
from PIL import Image,ImageTk
import tkinter as tk
from src.ASRBubble import ASRBubble

from configparser import ConfigParser
config = ConfigParser()
config.read('config.ini')

class TimerThread(threading.Thread):
    def __init__(self,h,m,s,target):
        threading.Thread.__init__(self)
        self.total = 0
        self.target = target
        self.total = 3600*h + 60*m + s
        print(h,m,s,self.total)
        ASRBubble(self.target,text="Timer set for {}:{}:{}".format(h,m,s))


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
                self.display(self.target)
        finally:
            print('ended')

    def display(self, target):
        print("alarm triggered")
        
        alarmFrame = tk.Label(target,image=self.img,text = "\n\nDouble click to close.",fg="blue",bg="beige")
        alarmFrame.image = self.img
        alarmFrame.place(in_=target,x=-1,y=-1,anchor="nw")

        alarmFrame.bind('<Double-Button-1>', lambda x: alarmFrame.destroy())