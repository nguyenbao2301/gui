import tkinter as tk
import time
from src.KeywordThread import KeywordThread
from configparser import ConfigParser
from src.utils import reduceOpacity
from PIL import Image,ImageTk

config = ConfigParser()
config.read('config.ini')
# config.add_section('main')

class TestingPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        controller.geometry("400x400")
        self.sensitivity = tk.DoubleVar()

        self.sensitivity.set(config.get('main','sensitivity'))
        self.pattern_dir = config.get('main','pattern_dir')

        self.img_path = config.get('main','img')
        self.img2_path = config.get('main','img2')
        self.opacity = float(config.get('main','img_opacity'))
        img= (Image.open(self.img_path))
        img.thumbnail((150,150))
        img = reduceOpacity(img,self.opacity*0.01)
        self.img= ImageTk.PhotoImage(img)

        img2= (Image.open(self.img2_path))
        img2.thumbnail((150,150))
        self.img2= ImageTk.PhotoImage(img2)

        self.frameL = tk.Frame(self,width=200,height=250,border=10,bg="white")
        self.frameL.pack_propagate(0)
        self.frameR = tk.Frame(self,width=150,height=150,bg="white")
        self.imgLabel = tk.Label(self.frameR,image=self.img)
        self.imgLabel.pack(fill="both",expand=True)
        self.imgLabel.image = self.img

        self.label = tk.Label(self.frameL,justify="left",bg="white",text = "Try saying your keyword and some other things.\nThe panel on the right will change color when it detects something.\nAdjust the sensitivity so that only keywords are detected.",wraplength=180)

        button_next = tk.Button(self,text="Finish",command = lambda: controller.show_frame("FinishPage"),relief=tk.GROOVE)
        self.slider = tk.Scale(self,from_= 0, to=10.0, orient="horizontal",variable=self.sensitivity,resolution=0.1,length=350)

        self.sensitivity.trace("w",self.update)

        self.frameL.grid(row=0,columnspan=2,padx=10,pady=10)
        self.frameR.grid(row=0,column=2,padx=10,pady=10)
        self.slider.grid(row=1,columnspan=3,pady=10)
        self.label.pack()
        button_next.grid(row=2,column=2,pady=20,padx=15,ipadx = 20,sticky="ew")

        self.thread = KeywordThread(self.process)
        self.thread.daemon = True
        self.thread.start()




    def update(self,*args):
        config.read('config.ini')
        config.set('main','sensitivity',str(self.sensitivity.get()))
        print("saved ",str(self.sensitivity.get()))
        with open('config.ini', 'w') as f:
            config.write(f)
            f.close()

    def process(self):
        
        self.imgLabel.configure(image=self.img2)
        self.imgLabel.image = self.img2
        self.imgLabel.update()
        time.sleep(1)
        self.imgLabel.config(image=self.img)
        self.imgLabel.image = self.img
        self.imgLabel.update()

    def on_switch(self):
        self.thread.raise_exception()
        self.thread.join()
