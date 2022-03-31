from cgitb import reset
import tkinter as tk
from PIL import Image,ImageTk
from src.KeywordThread import KeywordThread
from src.MenuPage import MenuPage
from src.utils import reduceOpacity
from src.ASRBubble import ASRBubble
from src.processor import recognize
from src.IDSF import IDSF
from src.alarm import AlarmThread
from src.timer import TimerThread
import speech_recognition as sr

from configparser import ConfigParser
config = ConfigParser()
config.read('config.ini')

class MainApp(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.sensitivity = config.get('main','sensitivity')
        self.pattern_dir = config.get('main','pattern_dir')
        self.img_path = config.get('main','img')
        self.img2_path = config.get('main','img2')

        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.idsf = IDSF()

        w,h = int(config.get("main","width")),int(config.get("main","height"))
        
        img= (Image.open(self.img_path))
        img= img.resize((w,h), Image.ANTIALIAS)
        img = reduceOpacity(img,float(0.01*float(config.get('main','img_opacity'))))
        self.img= ImageTk.PhotoImage(img)

        img2= (Image.open(self.img2_path))
        img2= img2.resize((w,h), Image.ANTIALIAS)
        self.img2= ImageTk.PhotoImage(img2)

       

        self.grip = tk.Label(self,image=self.img,bg = 'beige')
        self.grip.image = self.img
        self.grip.pack(side="left", fill="both",expand=True)

        
        
        self.setSize(w,h)
         
        self.grip.bind("<ButtonPress-1>", self.start_move)
        self.grip.bind("<ButtonRelease-1>", self.stop_move)
        self.grip.bind("<B1-Motion>", self.do_move)

        self.grip.bind('<Double-Button-1>', self.start)
        self.grip.bind("<ButtonPress-3>", self.test )
        

        self.thread = KeywordThread(self.process)
        self.thread.daemon = True
        self.thread.start()

        self.AlarmThread = AlarmThread(self)
        self.AlarmThread.daemon = True
        self.AlarmThread.start()

       

        controller.overrideredirect(True)
        controller.wm_attributes("-topmost",True)
        controller.wm_attributes("-transparent","beige")
        controller.config(bg = "beige")
        self.menu_opened = False

        

        

    def test(self,*args):
        ASRBubble(self,text= "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAa")

    def start_move(self, event):
        self.controller.x = event.x
        self.controller.y = event.y

    def stop_move(self, event):
        self.controller.conx = None
        self.controller.y = None

    def do_move(self, event):
        deltax = event.x - self.controller.x
        deltay = event.y - self.controller.y
        x = self.controller.winfo_x() + deltax
        y = self.controller.winfo_y() + deltay
        x = 0 if x<0 else x
        y= 0 if y<0 else y
        x= self.controller.winfo_screenwidth()-150 if x>self.controller.winfo_screenwidth()-150 else x
        y= self.controller.winfo_screenheight()-150 if y>self.controller.winfo_screenheight()-150 else y
        self.controller.geometry(f"+{x}+{y}")

    def start(self,*args):
        print("D")
        if(self.menu_opened==False):
            MenuPage(self)

    def process(self):
        print(self.menu_opened)
        if self.grip.image == self.img: #Not already active
            if self.menu_opened == False:
                self.grip.configure(image=self.img2)
                self.grip.image = self.img2
                self.grip.update()
                # self.grip.after(500,self.resetImg)
                recognize(self,self.recognizer,self.microphone,self.idsf)
                self.resetImg()
                # time.sleep(2)
                

    def resetImg(self):
        #  if self.grip.image != self.img: #Not already active
                self.grip.configure(image=self.img)
                self.grip.image = self.img
                self.grip.update()

    def setSize(self,w,h):
        if w< 50:
            w = 50
        if h<50:
            h = 50
        controller = self.controller
        controller.geometry("{}x{}".format(w,h))
        controller.minsize(w,h)
        controller.maxsize(w,h)

        img= (Image.open(self.img_path))
        img= img.resize((w,h), Image.ANTIALIAS)
        img = reduceOpacity(img,float(0.01*float(config.get('main','img_opacity'))))
        self.img= ImageTk.PhotoImage(img)

        img2= (Image.open(self.img2_path))
        img2= img2.resize((w,h), Image.ANTIALIAS)
        self.img2= ImageTk.PhotoImage(img2)

        self.resetImg()

    def setTimer(self,_time):
        temp  = _time.split(':')
        h = int(temp[0]) if temp[0]!= '' else 0
        m = int(temp[1]) if temp[1]!= '' else 0
        s = int(temp[2]) if temp[2]!= '' else 0
        print(h,m,s)
        Timer = TimerThread(h,m,s,self)
        Timer.daemon = True
        Timer.start()

    def on_switch(self):
        return