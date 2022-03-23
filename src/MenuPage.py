
import tkinter as tk
import time
import os
from winsound import PlaySound
from PIL import Image,ImageTk

from src.utils import reduceOpacity,restartThread,browse,clearDir
from src.KeywordThread import KeywordThread
from src.RecordPage import RecordToplevel
from tkinter import filedialog


from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')

curMenu = None
curDir = ""
trigger = 0

class Genreral(tk.Frame):
    def __init__(self, parent,master):
        tk.Frame.__init__(self)
        # self.label = tk.Label(parent,text="This is the general menu")
        # self.label.pack(fill="both",expand=True)
        global config
        config.read('config.ini')
        self.parent = parent
        self.master = master
        self.opacity = tk.DoubleVar()
        self.opacity.set(config.get('main','img_opacity'))
        self.opacity.trace("w",self.changeOpacity)

        self.img_path = config.get('main','img')
        self.img2_path = config.get('main','img2')

        img= (Image.open(self.img_path))
        img= img.resize((100,100), Image.ANTIALIAS)
        img = reduceOpacity(img,self.opacity.get()*0.01)
        self.img= ImageTk.PhotoImage(img)

        img2= (Image.open(self.img2_path))
        img2= img2.resize((100,100), Image.ANTIALIAS)
        self.img2= ImageTk.PhotoImage(img2)

        self.img1Title = tk.Label(parent,text="Image (Inactive)")
        self.img1DisplayFrame = tk.Frame(parent,width=100,height=100,bg= "beige")
        self.img1DisplayFrame.pack_propagate(0)
        self.img1DisplayLabel = tk.Label(self.img1DisplayFrame,image=self.img)
        self.img1DisplayLabel.image= self.img
        self.img1DisplayLabel.pack(fill='both',expand=True)
        self.img1DisplayLabel.bind("<ButtonPress-1>",lambda x: self.changeImage('img'))

        self.img1Title.grid(row =0,column=0,padx=10,pady=10,sticky="new")
        self.img1DisplayFrame.grid(row= 0,rowspan=2,column=1,columnspan=2,padx=10,pady=10)

        self.img2Title = tk.Label(parent,text="Image (Active)")
        self.img2DisplayFrame = tk.Frame(parent,width=100,height=100,bg= "white")
        self.img2DisplayFrame.pack_propagate(0)
        self.img2DisplayLabel = tk.Label(self.img2DisplayFrame,image=self.img2)
        self.img2DisplayLabel.image= self.img2
        self.img2DisplayLabel.pack(fill='both',expand=True)
        self.img2DisplayLabel.bind("<ButtonPress-1>",lambda x: self.changeImage('img2'))

        self.img2Title.grid(row =3,column=0,padx=10,pady=10,sticky="new")
        self.img2DisplayFrame.grid(row= 3,rowspan=2,column=1,columnspan=2,padx=10,pady=10)
    

        self.opacityTitle = tk.Label(parent,text = "Image opactity (Inactive")
        self.opacitySlider = tk.Scale(parent,from_= 0, to=100, orient="horizontal",variable=self.opacity,resolution=1,length=350)

        self.opacityTitle.grid(row=5,column=0,padx=10,pady=10,sticky="ew")
        self.opacitySlider.grid(row=6,column=0,padx=10,pady=10,sticky="ew")

    def changeOpacity(self,*args):
        global config
        config.read('config.ini')

        self.img_path = config.get('main','img')
        img= (Image.open(self.img_path))
        img= img.resize((100,100), Image.ANTIALIAS)
        img = reduceOpacity(img,self.opacity.get()*0.01)
        img = ImageTk.PhotoImage(img)


        self.img1DisplayLabel.config(image= img)
        self.img1DisplayLabel.image = img
        self.img1DisplayLabel.update()

        img= (Image.open(self.img_path))
        img= img.resize((150,150), Image.ANTIALIAS)
        img = reduceOpacity(img,self.opacity.get()*0.01)
        img = ImageTk.PhotoImage(img)

        self.master.grip.config(image= img)
        self.master.grip.image = img
        self.master.grip.update()

        
        config.set('main','img_opacity',str(self.opacity.get()))
        print("saved ",str(self.opacity.get()))
        with open('config.ini', 'w') as f:
            config.write(f)
            f.close()
        
    def changeImage(self,tag,*args):
        print(tag)
        global config
        config.read('config.ini')
        img_file = filedialog.askopenfile(filetypes=[('Image Files', ['.jpeg', '.jpg', '.png', '.gif','.tiff', '.tif', '.bmp'])])
        if not img_file:
            return
        img_file = os.path.normpath(img_file.name)
        

        
        img= (Image.open(img_file))
        img= img.resize((100,100), Image.ANTIALIAS)
        
        img = ImageTk.PhotoImage(img)
        label = self.img1DisplayLabel if tag == 'img' else self.img2DisplayLabel
        label.config(image = img)
        label.image = img
        label.update()
        

        
        
        config.set('main',tag,str(img_file))
        print("saved ",str(img_file))
        with open('config.ini', 'w') as f:
            config.write(f)
            f.close()

        

        w,h = int(config.get("main","width")),int(config.get("main","height"))
        self.master.setSize(w,h)

        self.changeOpacity()
        
        return


class Keyword(tk.Frame):
    def __init__(self, parent,master = None):
        tk.Frame.__init__(self)
        global config
        config.read('config.ini')
        self.parent = parent
        self.master = master
        self.menu_opened = False
        self.sensitivity = tk.DoubleVar()
        self.sensitivity.set(config.get('main','sensitivity'))

        self.pattern_dir = tk.StringVar()
        self.pattern_dir.set(config.get('main','pattern_dir'))
        # self.pattern_dir.trace("w",self.changePatternDir)

        self.temp_dir = tk.StringVar()
        self.temp_dir.set(config.get('main','temp_dir'))
        # self.temp_dir.trace("w",self.changeTempDir)

        self.sensitivity.trace("w",self.changeSensitivity)

        # self.label = tk.Label(parent,text="This is the keyword menu")
        # self.label.pack(fill="both",expand=True)
        self.pack_propagate(0)

        self.recordLabel = tk.Label(parent, text = "Record Keyword",justify="left")
        self.recordButton = tk.Button(parent,text="Record",command=self.openRecord)

        self.recordLabel.grid(sticky= "ew",row=0,column=0,padx=10,pady=10)
        self.recordButton.grid(row=0,column=1,columnspan=2,padx=10,pady=10,sticky="ew")

        self.sensitivityFrame = tk.Frame(parent,width=100,height=100,bg= "blue")
        self.sensitivityTitle = tk.Label(parent,text="Adjust Sensitivity",justify='left')
        self.sensitivitySlider = tk.Scale(parent,from_= 0, to=5.0, orient="horizontal",variable=self.sensitivity,resolution=0.1,length=350)

        self.sensitivityTitle.grid(sticky= "ew",row=1,column=0,padx=10,pady=10)
        self.sensitivitySlider.grid(row=2,column=0,padx=10,pady=10)
        self.sensitivityFrame.grid(row= 1,rowspan=2,column=1,columnspan=2,padx=10,pady=10)

        self.patternTitle = tk.Label(parent,text="Audio Pattern Dir",justify='left')
        self.patternEntry = tk.Entry(parent,textvariable=self.pattern_dir,width=25)
        self.patternButton = tk.Button(parent,text="Browse",command=lambda: browse(self.changePatternDir,config.get('main','pattern_dir')))
        self.patternClear = tk.Button(parent,text="Clear",command=lambda: clearDir(config.get('main','pattern_dir')))

        self.patternTitle.grid(row=3,column=0,padx=10,pady=10,sticky = "ew")
        self.patternEntry.grid(row=4,column=0,padx=10,pady=10,sticky="ew")
        self.patternButton.grid(row=4,column=1,padx=10,pady=10,sticky="ew")
        self.patternClear.grid(row=4,column=2,padx=10,pady=10,sticky="ew")


        self.tempTitle = tk.Label(parent,text="Temp Audio Dir",justify='left')
        self.tempEntry = tk.Entry(parent,textvariable=self.temp_dir,width=25)
        self.tempButton = tk.Button(parent,text="Browse",command=lambda: browse(self.changeTempDir,config.get('main','temp_dir')))
        # self.tempClear = tk.Button(parent,text="Clear",command=lambda: clearDir(config.get('main','pattern_dir')))

        self.tempTitle.grid(row=5,column=0,padx=10,pady=10,sticky = "ew")
        self.tempEntry.grid(row=6,column=0,padx=10,pady=10,sticky="ew")
        self.tempButton.grid(row=6,column=1,columnspan=2,padx=10,pady=10,sticky="ew")
        # self.patternClear.grid(row=3,column=2,padx=10,pady=10,sticky="ew")


        self.thread = KeywordThread(func = self.process)
        self.thread.daemon = True
        self.thread.start()

    def openRecord(self,*args):
        # print(self.menu_opened)
        if(self.menu_opened==False):
            RecordToplevel(self)

    def changeSensitivity(self,*args):
        global config
        config.read('config.ini')
        config.set('main','sensitivity',str(self.sensitivity.get()))
        print("saved ",str(self.sensitivity.get()))
        with open('config.ini', 'w') as f:
            config.write(f)
            f.close()

    def changePatternDir(self,curDir="",*args):
            self.pattern_dir.set(str(curDir))
            config.set('main','pattern_dir',str(curDir))
            print("saved ",str(curDir))
            with open('config.ini', 'w') as f:
                config.write(f)
            restartThread()

    def changeTempDir(self,curDir="",*args):
            self.temp_dir.set(str(curDir))
            config.set('main','temp_dir',str(curDir))
            print("saved ",str(curDir))
            with open('config.ini', 'w') as f:
                config.write(f)
            restartThread()

    def process(self):
        print("running")
        global curMenu
        try:
            if hasattr(self,"sensitivityFrame"):
                self.sensitivityFrame.configure(bg="green")
                        # print(self.sensitivity.get())
                time.sleep(1)
                self.sensitivityFrame.configure(bg="blue")
        finally:
            return
        
class AlarmTimer(tk.Frame):
    def __init__(self, parent,master):
        tk.Frame.__init__(self)
        global config
        config.read('config.ini')
        self.parent = parent
        self.master = master
      
        self.img_path = config.get('main','alarm_img')
        self.img2_path = config.get('main','timer_img')

        self.alarm_dir = tk.StringVar()
        self.alarm_dir.set(config.get('main','alarm_dir'))
        self.alarmVolume = tk.DoubleVar()
        self.alarmVolume.set(config.get('main','timer_volume'))
        self.alarmVolume.trace("w",self.changeAlarmVolume)

        self.timer_dir = tk.StringVar()
        self.timer_dir.set(config.get('main','timer_dir'))
        self.timerVolume = tk.DoubleVar()
        self.timerVolume.set(config.get('main','timer_volume'))
        self.timerVolume.trace("w",self.changeTimerVolume)

        img= (Image.open(self.img_path))
        img= img.resize((100,100), Image.ANTIALIAS)
        self.img= ImageTk.PhotoImage(img)

        img2= (Image.open(self.img2_path))
        img2= img2.resize((100,100), Image.ANTIALIAS)
        self.img2= ImageTk.PhotoImage(img2)

        self.img1Title = tk.Label(parent,text="Image (Alarm)")
        self.img1DisplayFrame = tk.Frame(parent,width=100,height=100,bg= "beige")
        self.img1DisplayFrame.pack_propagate(0)
        self.img1DisplayLabel = tk.Label(self.img1DisplayFrame,image=self.img)
        self.img1DisplayLabel.image= self.img
        self.img1DisplayLabel.pack(fill='both',expand=True)
        self.img1DisplayLabel.bind("<ButtonPress-1>",lambda x: self.changeImage('alarm_img'))

        self.img1Title.grid(row =0,column=0,padx=10,pady=10,sticky="new")
        self.img1DisplayFrame.grid(row= 0,rowspan=2,column=1,columnspan=2,padx=10,pady=10,sticky = "e")

        self.img2Title = tk.Label(parent,text="Image (Timer)")
        self.img2DisplayFrame = tk.Frame(parent,width=100,height=100,bg= "white")
        self.img2DisplayFrame.pack_propagate(0)
        self.img2DisplayLabel = tk.Label(self.img2DisplayFrame,image=self.img2)
        self.img2DisplayLabel.image= self.img2
        self.img2DisplayLabel.pack(fill='both',expand=True)
        self.img2DisplayLabel.bind("<ButtonPress-1>",lambda x: self.changeImage('timer_img'))

        self.img2Title.grid(row =3,column=0,padx=10,pady=10,sticky="new")
        self.img2DisplayFrame.grid(row= 3,rowspan=2,column=1,columnspan=2,padx=10,pady=10)

        self.alarmTitle = tk.Label(parent,text="Alarm Audio",justify='left')
        self.alarmEntry = tk.Entry(parent,textvariable=self.alarm_dir,width=25)
        self.alarmButton = tk.Button(parent,text="Browse",command=lambda: browse(self.changeAlarm,config.get('main','temp_dir')))
        self.alarmPlay = tk.Button(parent,text="Play",command=lambda: PlaySound(self.alarm_dir.get()))
        

        self.alarmTitle.grid(row=5,column=0,padx=10,pady=10,sticky = "ew")
        self.alarmEntry.grid(row=6,column=0,padx=10,pady=10,sticky="ew")
        self.alarmButton.grid(row=6,column=1,padx=10,pady=10,sticky="ew")
        self.alarmPlay.grid(row=6,column=2,padx=10,pady=10,sticky="ew")

        self.alarmVolumeTitle = tk.Label(parent,text = "Alarm Volume")
        self.alarmVolumeSlider = tk.Scale(parent,from_= 0, to=100, orient="horizontal",variable=self.alarmVolume,resolution=1,length=350)

        self.alarmVolumeTitle.grid(row=7,column=0,padx=10,pady=10,sticky="ew")
        self.alarmVolumeSlider.grid(row=8,column=0,padx=10,pady=10,sticky="ew")

        self.timerTitle = tk.Label(parent,text="Timer Audio",justify='left')
        self.timerEntry = tk.Entry(parent,textvariable=self.alarm_dir,width=25)
        self.timerButton = tk.Button(parent,text="Browse",command=lambda: browse(self.changeAlarm,config.get('main','temp_dir')))
        self.timerPlay = tk.Button(parent,text="Play",command=lambda: PlaySound(self.timer_dir.get()))

        self.timerTitle.grid(row=9,column=0,padx=10,pady=10,sticky = "ew")
        self.timerEntry.grid(row=10,column=0,padx=10,pady=10,sticky="ew")
        self.timerButton.grid(row=10,column=1,padx=10,pady=10,sticky="ew")
        self.timerPlay.grid(row=10,column=2,padx=10,pady=10,sticky="ew")

        self.timerVolumeTitle = tk.Label(parent,text = "Timer Volume")
        self.timerVolumeSlider = tk.Scale(parent,from_= 0, to=100, orient="horizontal",variable=self.alarmVolume,resolution=1,length=350)

        self.timerVolumeTitle.grid(row=11,column=0,padx=10,pady=10,sticky="ew")
        self.timerVolumeSlider.grid(row=12,column=0,padx=10,pady=10,sticky="ew")
    

    def changeAlarmVolume(self,*args):
        return

    def changeTimerVolume(self,*args):
        return

    def changeAlarm(self,curDir,*args):
        return
    def changeTimer(self,curDir,*args):
        return
    def changeImage(self,tag,*args):
        print(tag)
        global config
        config.read('config.ini')
        img_file = filedialog.askopenfile(filetypes=[('Image Files', ['.jpeg', '.jpg', '.png', '.gif','.tiff', '.tif', '.bmp'])])
        if not img_file:
            return
        img_file = os.path.normpath(img_file.name)
        

        
        img= (Image.open(img_file))
        img= img.resize((100,100), Image.ANTIALIAS)
        
        img = ImageTk.PhotoImage(img)
        label = self.img1DisplayLabel if tag == 'alarm_img' else self.img2DisplayLabel
        label.config(image = img)
        label.image = img
        label.update()

        config.set('main',tag,str(img_file))
        print("saved ",str(img_file))
        with open('config.ini', 'w') as f:
            config.write(f)
            f.close()
        
        return

class SearchWeather(tk.Frame):
    def __init__(self, parent,master = None):
        tk.Frame.__init__(self)
        self.label = tk.Label(parent,text="This is the search/weather menu")
        self.label.pack(fill="both",expand=True)
    
        
class MenuPage(tk.Toplevel):
    def __init__(self, master =None):
        super().__init__(master = master)
        
        self.title("New Window")
        self.geometry("900x600")
        global curMenu
        self.master = master
        self.protocol("WM_DELETE_WINDOW", self.close)

        self.frameL = tk.Frame(self,width=250,border=10,bg="white")
       
        self.frameR = tk.Frame(self,border=10,bg="Slategray1")
        self.frameR.pack_propagate(0)
        curMenu = Genreral(self.frameR,self.master)
      
        #General menu
        self.frame1 = tk.Frame(self.frameL,width= 250,height=75,border=5,bg="SkyBlue1")
        self.frame1.pack_propagate(0)
        self.frame1.bind("<ButtonPress-1>",lambda x: self.changeMenu(Genreral))
        

        self.frame2 = tk.Frame(self.frameL,width= 250,height=75,border=0,bg="SkyBlue3")
        self.frame2.pack_propagate(0)
        self.frame2.bind("<ButtonPress-1>",lambda x: self.changeMenu(Keyword))

        self.frame3 = tk.Frame(self.frameL,width= 250,height=75,border=0,bg="SkyBlue1")
        self.frame3.pack_propagate(0)

        self.frame4 = tk.Frame(self.frameL,width= 250,height=75,border=0,bg="SkyBlue3")
        self.frame4.pack_propagate(0)

        self.frame_exit = tk.Frame(self.frameL,width= 250,height=75,border=0,bg="tomato3")
        self.frame_exit.pack_propagate(0)
        self.frame_exit.bind("<ButtonPress-1>",self.exit)

        img1= ImageTk.PhotoImage(Image.open('img/button_1.png').resize((250,75)))
        self.label1 = tk.Label(self.frame1,text = "General",image=img1)
        self.label1.image =  img1
        self.label1.bind("<ButtonPress-1>",lambda x: self.changeMenu(Genreral))

        img2= ImageTk.PhotoImage(Image.open('img/button_2.png').resize((250,75)))
        self.label2 = tk.Label(self.frame2,text = "Keyword",image=img2)
        self.label2.image =  img2
        self.label2.bind("<ButtonPress-1>",lambda x: self.changeMenu(Keyword))

        img3= ImageTk.PhotoImage(Image.open('img/button_3.png').resize((250,75)))
        self.label3 = tk.Label(self.frame3,text = "Alarm / Timer",image= img3)
        self.label3.bind("<ButtonPress-1>",lambda x: self.changeMenu(AlarmTimer))
        self.label3.image =  img3

        img4= ImageTk.PhotoImage(Image.open('img/button_4.png').resize((250,75)))
        self.label4 = tk.Label(self.frame4,text = "Search / Weather",image=img4)
        self.label4.bind("<ButtonPress-1>",lambda x: self.changeMenu(SearchWeather))
        self.label4.image =  img4

        img5= ImageTk.PhotoImage(Image.open('img/button_5.png').resize((250,75)))
        self.label_exit = tk.Label(self.frame_exit, text = "Exit Program",image=img5)
        self.label_exit.bind("<ButtonPress-1>",self.exit)
        self.label_exit.image =  img5

        self.frame1.pack(side="top",pady = 5)
        self.frame2.pack(pady = 5)
        self.frame3.pack(pady = 5)
        self.frame4.pack(pady = 5)
        self.frame_exit.pack(side="bottom",fill="x")

        self.label1.pack(padx= 0,pady =0, fill="both",expand=True)
        self.label2.pack(padx= 0,pady =0, fill="both",expand=True)
        self.label3.pack(padx= 0,pady =0, fill="both",expand=True)
        self.label4.pack(padx= 0,pady =0, fill="both",expand=True)
        self.label_exit.pack(padx= 0,pady =0, fill="both",expand=True)

        self.frameL.pack(side="left",fill="y")
        self.frameR.pack(side="right",fill="both",expand=True)  

        self.master.menu_opened = True
        

    def clear(self):
        for widget in self.frameR.winfo_children():
            widget.destroy()

    def changeMenu(self,frame):
        global curMenu
        if hasattr(curMenu,'thread'):
            curMenu.thread.raise_exception()
            curMenu.thread.join()
        curMenu.destroy()
        global trigger
        trigger = -1
        for widget  in self.frameR.winfo_children():
            widget.destroy()
        
        curMenu = frame(self.frameR,master=self.master)


    def close(self,*args):
        print("closing")
        global curMenu
        curMenu = None
        self.master.menu_opened = False
        self.master.controller.overrideredirect(False)
        self.master.controller.overrideredirect(True)
        self.destroy()

    def exit(self,*args):
        if tk.messagebox.askyesno("Confirmation","Exit the program?"):
            self.master.quit()
            self.destroy()

