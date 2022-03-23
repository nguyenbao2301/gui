import time
from datetime import date, datetime
import threading 
import tkinter as tk
from PIL import Image,ImageTk

from configparser import ConfigParser
config = ConfigParser()
config.read('config.ini')

class AlarmThread(threading.Thread):
    def __init__(self,target):
        threading.Thread.__init__(self)
        self.target = target
        
        img_path = "./img/alarm_overlay.png"
        w,h = int(config.get("main","width")),int(config.get("main","height"))
        img= (Image.open(img_path))
        img= img.resize((w,h),resample=Image.LANCZOS)
        # img = reduceOpacity(img,0.5)
        self.img= ImageTk.PhotoImage(img)

    def run(self):
        try:
            #wait til XX:XX:00
            while True:
                now = int(datetime.now().strftime('%S'))
                if now == 0:
                    break
            while True:
                arr = self.load()
                today = date.today().strftime('%d/%m')
                now = datetime.now().strftime('%H:%M')
                
                for _day,_time in arr:
                    if _day == 'X':
                        self.checkTime(_time,now)
                    elif len(_day) == 1:
                        if date.today().weekday() == int(_day):
                            self.checkTime(_time,now)
                    elif _day in today:
                        self.checkTime(_time,now)
                time.sleep(60)
        finally:
            print('ended')

    def load(self):
        arr = []
        file = open('./alarms.txt',"r")
        lines = file.readlines()
        for line in lines:
            sp = line.split()
            _day,_time = sp[0],sp[1]
            arr.append((_day,_time))
        return arr

    def display(self, target):
        print("alarm triggered")
    
        alarmFrame = tk.Label(target,image=self.img,text = "\n\nDouble click to close.",fg="blue",bg="beige")
        alarmFrame.image = self.img
        # alarmFrame.wm_attributes("-transparent","beige")
        alarmFrame.place(in_=target,x=-1,y=-1,anchor="nw")

        alarmFrame.bind('<Double-Button-1>', lambda x: alarmFrame.destroy())

    def checkTime(self,_time,now):
        # print(now,_time)
        if now == _time: 
            self.display(self.target)


def addAlarm(_day,_time):
    file = open("alarms.txt","a")
    file.write(_day + " " + _time + "\n")
