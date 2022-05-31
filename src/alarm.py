import time
from datetime import date, datetime
import threading 
import tkinter as tk
from PIL import Image,ImageTk
from configparser import ConfigParser
from audioplayer import AudioPlayer
config = ConfigParser()
config.read('config.ini')

class AlarmThread(threading.Thread):
    def __init__(self,target):
        threading.Thread.__init__(self)
        self.target = target
        self.audio = None
        self.flag = True
        img_path = "./img/alarm_overlay.png"
        w,h = int(config.get("main","width")),int(config.get("main","height"))
        img= (Image.open(img_path))
        img= img.resize((w,h),resample=Image.LANCZOS)
        # img = reduceOpacity(img,0.5)
        self.img= ImageTk.PhotoImage(img)

    def run(self):
        try:
            #wait til XX:XX:00
            self.wait()
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
            if self.audio != None:
                self.audio.close()
            print('ended')

    def wait(self):
        while True:
                time.sleep(0.001)
                now = int(datetime.now().strftime('%S'))
                if now == 0:
                    break
        return
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

        alarmFrame.bind('<Double-Button-1>', lambda x: self.close(alarmFrame))

        # self.display(self.target)


        


        

    def checkTime(self,_time,now):
        # print(now,_time)
        if now == _time: 
            self.display(self.target)

            
            try:
                print("playing audio")
                if self.audio == None:
                    _audio = config.get('main','alarm_dir')
                    _volume = int(config.get('main','alarm_volume'))
                    self.audio = AudioPlayer(_audio)
                    self.audio.volume = _volume
                    self.audio.play(loop=True)
            except Exception:
                print("audio alarm error")

            while(self.flag):
                continue
            if self.audio != None:
                self.audio.stop()
                self.flag = True

        self.audio = None
        self.wait()

    def close(self,frame):
        self.flag = False
        frame.destroy()

def addAlarm(_day,_time):
    file = open("alarms.txt","a")
    file.write(_day + " " + _time + "\n")
