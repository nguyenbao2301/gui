import tkinter as tk
from tkinter import messagebox
import time
import os
from PIL import Image,ImageTk
from src.utils import reduceOpacity,restartThread,browse,PlaySound
from src.KeywordThread import KeywordThread
from src.RecordPage import RecordToplevel
from tkinter import filedialog
import re
import codecs

from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini',encoding='utf-8')

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
        self.opacity.trace_add("write",self.changeOpacity)

        self.img_path = config.get('main','img')
        self.img2_path = config.get('main','img2')

        img= (Image.open(self.img_path))
        img.thumbnail((100,100))
        img = reduceOpacity(img,self.opacity.get()*0.01)
        self.img= ImageTk.PhotoImage(img)

        img2= (Image.open(self.img2_path))
        img2.thumbnail((100,100))
        self.img2= ImageTk.PhotoImage(img2)

        self.imgFrame = tk.LabelFrame(parent,text = "Hình ảnh chính" )
        self.imgFrame.grid_columnconfigure(0,weight=1)
        self.imgFrame.grid_columnconfigure(1,weight=1)
        self.imgFrame.grid_rowconfigure(0,weight=1)
        self.imgFrame.grid_rowconfigure(1,weight=1)

        self.img1Title = tk.Label(self.imgFrame,text="Chế độ chờ")
        self.img1DisplayFrame = tk.Frame(self.imgFrame,width=100,height=100,bg= "beige")
        self.img1DisplayFrame.pack_propagate(0)
        self.img1DisplayLabel = tk.Label(self.img1DisplayFrame,image=self.img)
        self.img1DisplayLabel.image= self.img
        self.img1DisplayLabel.pack(fill='both',expand=True)
        self.img1DisplayLabel.bind("<ButtonPress-1>",lambda x: self.changeImage('img'))


        self.img2Title = tk.Label(self.imgFrame,text="Đang nghe lệnh")
        self.img2DisplayFrame = tk.Frame(self.imgFrame,width=100,height=100,bg= "white")
        self.img2DisplayFrame.pack_propagate(0)
        self.img2DisplayLabel = tk.Label(self.img2DisplayFrame,image=self.img2)
        self.img2DisplayLabel.image= self.img2
        self.img2DisplayLabel.pack(fill='both',expand=True)
        self.img2DisplayLabel.bind("<ButtonPress-1>",lambda x: self.changeImage('img2'))

        self.imgFrame.grid(row=0,column=0,sticky= "ew",padx = 10,pady =10,ipadx=10,ipady=10)

        self.img1Title.grid(row=0,column=0,sticky="ew",padx=10,pady=10)
        self.img2Title.grid(row=0,column=1,sticky="ew",padx=10,pady=10)
        self.img1DisplayFrame.grid(row=1,column=0,sticky="ew",padx=10,pady=(0,10))
        self.img2DisplayFrame.grid(row=1,column=1,sticky="ew",padx=10,pady=(0,10))
        
        self.opacityFrame = tk.LabelFrame(parent,text = "Độ mờ (Chế độ chờ)")
        self.opacitySlider = tk.Scale(self.opacityFrame,from_= 0, to=100, orient="horizontal",variable=self.opacity,resolution=1)

        self.opacityFrame.grid(row=1,column=0,padx=10,pady=10,sticky="ew",ipadx=10,ipady=10)
        self.opacitySlider.pack(fill="x",expand=True,padx =10)

        w,h = int(config.get("main","width")),int(config.get("main","height"))
        self.sizeVar = tk.StringVar(parent,value = "{}x{}".format(w,h))
        self.sizeVar.trace_add("write",self.changeSize)
        self.sizeFrame = tk.LabelFrame(parent,text = "Kích thước cửa sổ")
        self.sizeInput = tk.Entry(self.sizeFrame,textvariable= self.sizeVar,justify='center')

        self.sizeFrame.grid(row=2,column=0,padx=10,pady=10,sticky="ew",ipadx=10,ipady=10)
        self.sizeInput.pack(fill= "x",expand=True,padx =10)

        self.Volume = tk.IntVar()
        self.Volume.set(config.get('main','tts_volume'))
        self.Volume.trace_add("write",self.changeVolume)
        self.VolumeTitle = tk.LabelFrame(parent,text = "Âm lượng phản hồi")
        self.VolumeSlider = tk.Scale(self.VolumeTitle,from_= 0, to=100, orient="horizontal",variable=self.Volume,resolution=1,length=350)

        self.VolumeTitle.grid(row=3,column=0,padx=10,pady=10,sticky="ew",ipadx=10,ipady=10)
        self.VolumeSlider.pack(fill="x",expand=True,padx=10)

    def changeOpacity(self,*args):
        global config
        config.read('config.ini')

        config.set('main','img_opacity',str(self.opacity.get()))
        print("saved ",str(self.opacity.get()))
        with open('config.ini', 'w') as f:
            config.write(f)
            f.close()

        self.img_path = config.get('main','img')
        img= (Image.open(self.img_path))
        img.thumbnail((100,100))
        img = reduceOpacity(img,self.opacity.get()*0.01)
        img = ImageTk.PhotoImage(img)

        self.img1DisplayLabel.configure(image=img)
        self.img1DisplayLabel.image = img
        self.img1DisplayLabel.update()

        w,h = int(config.get("main","width")),int(config.get("main","height"))
        img= (Image.open(self.img_path))
        img= img.resize((w,h), Image.ANTIALIAS)
        img = reduceOpacity(img,float(0.01*float(config.get('main','img_opacity'))))
        self.master.img= ImageTk.PhotoImage(img)

        self.master.resetImg()       
    def changeImage(self,tag,*args):
        print(tag)
        global config
        config.read('config.ini')
        img_file = filedialog.askopenfile(filetypes=[('Image Files', ['.jpeg', '.jpg', '.png', '.gif','.tiff', '.tif', '.bmp'])])
        if not img_file:
            return
        img_file = os.path.normpath(img_file.name)
        

        
        img= (Image.open(img_file))
        img.thumbnail((100,100))
        
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
    def changeSize(self,*args):
        s = self.sizeVar.get()
        w,h = "",""
        if re.search("[0-9]+[x][0-9]+",s):
            try:
                t = s.split("x")
                w = int(t[0])
                h = int(t[1])
                if w>50 and h>50:
                    config.set('main','width',t[0])
                    config.set('main','height',t[1])
                    with open('config.ini', 'w') as f:
                        config.write(f)
                        f.close()
                    self.master.setSize(w,h)
                    return
            except:
                pass
    def changeVolume(self,*args):
        config.set('main','tts_volume',str(self.Volume.get()))
        with open('config.ini', 'w') as f:
            config.write(f)
            f.close()

class Keyword(tk.Frame):
    def __init__(self, parent,master = None):
        tk.Frame.__init__(self)
        global config
        config.read('config.ini')
        self.parent = parent
        self.master = master
        self.menu_opened = False

        self.img_path = config.get('main','img')
        self.img2_path = config.get('main','img2')
        self.opacity = float(config.get('main','img_opacity'))
        img= (Image.open(self.img_path))
        img.thumbnail((100,100))
        img = reduceOpacity(img,self.opacity*0.01)
        self.img= ImageTk.PhotoImage(img)

        img2= (Image.open(self.img2_path))
        img2.thumbnail((100,100))
        self.img2= ImageTk.PhotoImage(img2)

        self.sensitivity = tk.DoubleVar()
        self.sensitivity.set(config.get('main','sensitivity'))

        self.pattern_dir = tk.StringVar()
        self.pattern_dir.set(config.get('main','pattern_dir'))

        self.temp_dir = tk.StringVar()
        self.temp_dir.set(config.get('main','temp_dir'))

        self.sensitivity.trace_add("write",self.changeSensitivity)
        self.pack_propagate(0)

        self.recordFrame = tk.LabelFrame(parent,text = "Ghi âm từ khóa")
        self.recordFrame.columnconfigure(0,weight=2)
        self.recordFrame.columnconfigure(1,weight=1)
        self.recordLabel = tk.Label(self.recordFrame,text = "Ghi âm bộ từ khóa mới",anchor="w")
        self.recordButton = tk.Button(self.recordFrame,text="Ghi âm",relief=tk.GROOVE,command=self.openRecord)

        self.recordFrame.grid(row=0,column=0,padx=10,pady=10,sticky="ew",ipadx=10,ipady=10)
        self.recordLabel.grid(sticky= "ew",row=0,column=0,padx=10)
        self.recordButton.grid(row=0,column=1,padx=10,sticky="ew")

        self.sensitivityTitle = tk.LabelFrame(parent,text="Điều chỉnh độ nhạy")
        self.sensitivityTitle.columnconfigure(0,weight=1)
        self.sensitivityTitle.columnconfigure(1,weight=1)
        self.sensitivityFrame = tk.Frame(self.sensitivityTitle,width=100,height=100)
        self.sensitivityFrameL = tk.Label(self.sensitivityFrame,image=self.img)
        self.sensitivityFrameL.image = self.img
        self.sensitivityFrameL.pack(fill="both",expand=True)
        self.sensitivitySlider = tk.Scale(self.sensitivityTitle,from_= 0, to=10.0, orient="horizontal",variable=self.sensitivity,resolution=0.1,length=250)

        self.sensitivityTitle.grid(row=1,column=0,padx=10,pady=10,sticky="ew",ipadx=10)
        self.sensitivitySlider.grid(row=0,column=0,padx=10,pady=10,sticky="new")
        self.sensitivityFrame.grid(row= 0,column=1,pady=10)

        self.patternTitle = tk.LabelFrame(parent,text="Thư mục từ khóa")
        self.patternTitle.columnconfigure(0,weight=2)
        self.patternTitle.columnconfigure(1,weight=1)
        self.patternEntry = tk.Entry(self.patternTitle,textvariable=self.pattern_dir,width=25)
        self.patternButton = tk.Button(self.patternTitle,text="Chọn",relief=tk.GROOVE,command=lambda: browse(self.changePatternDir,config.get('main','pattern_dir')))
        # self.patternClear = tk.Button(self.patternTitle,text="Clear",relief=tk.GROOVE,command=lambda: clearDir(config.get('main','pattern_dir')))

        self.patternTitle.grid(row=2,column=0,padx=10,pady=10,sticky="ew",ipadx=10)
        self.patternEntry.grid(row=0,column=0,padx=10,pady=10,sticky="sew")
        self.patternButton.grid(row=0,column=1,padx=10,pady=10,sticky="sew")
        # self.patternClear.grid(row=0,column=2,padx=10,pady=10,sticky="sew")


        self.tempTitle = tk.LabelFrame(parent,text="Thư mục tạm")
        self.tempTitle.columnconfigure(0,weight=2)
        self.tempTitle.columnconfigure(1,weight=1)
        self.tempEntry = tk.Entry(self.tempTitle,textvariable=self.temp_dir,width=25)
        self.tempButton = tk.Button(self.tempTitle,text="Chọn",relief=tk.GROOVE,command=lambda: browse(self.changeTempDir,config.get('main','temp_dir')))

        self.tempTitle.grid(row=3,column=0,padx=10,pady=10,sticky="ew",ipadx=10)
        self.tempEntry.grid(row=0,column=0,padx=10,pady=10,sticky="ew")
        self.tempButton.grid(row=0,column=1,padx=10,pady=10,sticky="sew")
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
                self.sensitivityFrameL.configure(image=self.img2)
                self.sensitivityFrameL.image = self.img2
                        # print(self.sensitivity.get())
                time.sleep(1)
                self.sensitivityFrameL.configure(image=self.img)
                self.sensitivityFrameL.image = self.img
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
        self.alarmVolume = tk.IntVar()
        self.alarmVolume.set(config.get('main','timer_volume'))
        self.alarmVolume.trace_add("write",self.changeAlarmVolume)

        self.timer_dir = tk.StringVar()
        self.timer_dir.set(config.get('main','timer_dir'))
        self.timerVolume = tk.IntVar()
        self.timerVolume.set(config.get('main','timer_volume'))
        self.timerVolume.trace_add("write",self.changeTimerVolume)

        img= (Image.open(self.img_path))
        img.thumbnail((100,100))
        self.img= ImageTk.PhotoImage(img)

        img2= (Image.open(self.img2_path))
        img2.thumbnail((100,100))
        self.img2= ImageTk.PhotoImage(img2)

        self.imgFrame = tk.LabelFrame(parent,text = "Hình ảnh chuông báo" )
        self.imgFrame.grid_columnconfigure(0,weight=1)
        self.imgFrame.grid_columnconfigure(1,weight=1)
        self.imgFrame.grid_rowconfigure(0,weight=1)
        self.imgFrame.grid_rowconfigure(1,weight=1)

        self.img1Title = tk.Label(self.imgFrame,text="Báo thức")
        self.img1DisplayFrame = tk.Frame(self.imgFrame,width=100,height=100,bg= "beige")
        self.img1DisplayFrame.pack_propagate(0)
        self.img1DisplayLabel = tk.Label(self.img1DisplayFrame,image=self.img)
        self.img1DisplayLabel.image= self.img
        self.img1DisplayLabel.pack(fill='both',expand=True)
        self.img1DisplayLabel.bind("<ButtonPress-1>",lambda x: self.changeImage('alarm_img'))

        self.img2Title = tk.Label(self.imgFrame,text="Hẹn giờ")
        self.img2DisplayFrame = tk.Frame(self.imgFrame,width=100,height=100,bg= "white")
        self.img2DisplayFrame.pack_propagate(0)
        self.img2DisplayLabel = tk.Label(self.img2DisplayFrame,image=self.img2)
        self.img2DisplayLabel.image= self.img2
        self.img2DisplayLabel.pack(fill='both',expand=True)
        self.img2DisplayLabel.bind("<ButtonPress-1>",lambda x: self.changeImage('timer_img'))

        self.imgFrame.grid(row=0,column=0,sticky= "ew",padx = 10,pady =10,ipadx=10,ipady=10)
        self.img1Title.grid(row=0,column=0,sticky="ew",padx=10,pady=10)
        self.img2Title.grid(row=0,column=1,sticky="ew",padx=10,pady=10)
        self.img1DisplayFrame.grid(row=1,column=0,sticky="ew",padx=10,pady=(0,10))
        self.img2DisplayFrame.grid(row=1,column=1,sticky="ew",padx=10,pady=(0,10))

        self.alarmTitle = tk.LabelFrame(parent,text="Âm thanh báo thức")
        self.alarmTitle.grid_columnconfigure(0,weight=2)
        self.alarmTitle.grid_columnconfigure(1,weight=1)
        self.alarmTitle.grid_columnconfigure(2,weight=1)
        self.alarmEntry = tk.Entry(self.alarmTitle,textvariable=self.alarm_dir,width=25)
        self.alarmButton = tk.Button(self.alarmTitle,text="Browse",relief=tk.GROOVE,command=lambda: browse(self.changeAlarm,config.get('main','temp_dir')))
        self.alarmPlay = tk.Button(self.alarmTitle,text="Play",relief=tk.GROOVE,command=lambda: PlaySound(self.alarm_dir.get(),config.get('main','alarm_volume')))
        

        self.alarmTitle.grid(row=1,column=0,sticky= "ew",padx = 10,pady =10,ipadx=10,ipady=10)
        self.alarmEntry.grid(row=0,column=0,padx=10,sticky="sew")
        self.alarmButton.grid(row=0,column=1,padx=10,sticky="sew")
        self.alarmPlay.grid(row=0,column=2,padx=10,sticky="sew")

        self.alarmVolumeTitle = tk.LabelFrame(parent,text = "Âm lượng báo thức")
        self.alarmVolumeSlider = tk.Scale(self.alarmVolumeTitle,from_= 0, to=100, orient="horizontal",variable=self.alarmVolume,resolution=1,length=350)

        self.alarmVolumeTitle.grid(row=2,column=0,sticky= "ew",padx = 10,pady =10,ipadx=10,ipady=10)
        self.alarmVolumeSlider.pack(fill="x",expand=True,padx =10)

        self.timerTitle = tk.LabelFrame(parent,text="Âm thanh hẹn giờ")
        self.timerTitle.grid_columnconfigure(0,weight=2)
        self.timerTitle.grid_columnconfigure(1,weight=1)
        self.timerTitle.grid_columnconfigure(2,weight=1)
        self.timerEntry = tk.Entry(self.timerTitle,textvariable=self.alarm_dir,width=25)
        self.timerButton = tk.Button(self.timerTitle,text="Browse",relief=tk.GROOVE,command=lambda: browse(self.changeAlarm,config.get('main','temp_dir')))
        self.timerPlay = tk.Button(self.timerTitle,text="Play",relief=tk.GROOVE,command=lambda: PlaySound(self.timer_dir.get(),config.get('main','timer_volume')))

        self.timerTitle.grid(row=3,column=0,sticky= "ew",padx = 10,pady =10,ipadx=10,ipady=10)
        self.timerEntry.grid(row=0,column=0,padx=10,sticky="sew")
        self.timerButton.grid(row=0,column=1,padx=10,sticky="sew")
        self.timerPlay.grid(row=0,column=2,padx=10,sticky="sew")

        self.timerVolumeTitle = tk.LabelFrame(parent,text = "Âm lượng hẹn giờ")
        self.timerVolumeSlider = tk.Scale(self.timerVolumeTitle,from_= 0, to=100, orient="horizontal",variable=self.timerVolume,resolution=1,length=350)

        self.timerVolumeTitle.grid(row=4,column=0,sticky= "ew",padx = 10,pady =10,ipadx=10,ipady=10)
        self.timerVolumeSlider.pack(fill="x",expand=True,padx =10)

      
    

    def changeAlarmVolume(self,*args):
        config.set('main','alarm_volume',str(self.alarmVolume.get()))
        with open('config.ini', 'w') as f:
            config.write(f)
            f.close()

    def changeTimerVolume(self,*args):
        config.set('main','alarm_volume',str(self.timerVolume.get()))
        with open('config.ini', 'w') as f:
            config.write(f)
            f.close()

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
        img.thumbnail((100,100))
        
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
        
        parent.grid_columnconfigure(0,weight=1)
        self.searchEngine = tk.StringVar(parent,value = config.get("main","searchEngine"))
        self.searchEngine.trace_add("write",self.changeEngine)
        self.engineFrame = tk.LabelFrame(parent,text = "Công cụ tìm kiếm")
        self.engineEntry = tk.Entry(self.engineFrame,textvariable=self.searchEngine)

        self.engineFrame.grid(row=0,column=0,sticky= "ew",padx = 10,pady =10,ipadx=10,ipady=10)
        self.engineEntry.pack(fill="x",expand=True,padx=10)

        self.location = tk.StringVar(parent,value = bytes(config.get("main","location"),encoding='utf-8').decode('utf-8'))
        self.location.trace_add("write",self.changeLocation)
        self.locationFrame =tk.LabelFrame(parent,text="Địa điểm")
        self.locationEntry = tk.Entry(self.locationFrame,textvariable=self.location)
        self.locationFrame.grid(row=1,column=0,sticky= "ew",padx = 10,pady =10,ipadx=10,ipady=10)
        self.locationEntry.pack(fill="x",expand=True,padx=10)

        self.browser = tk.StringVar(parent,"Mặc định") 
        self.patternTitle = tk.LabelFrame(parent,text="Trình duyệt")
        self.patternTitle.columnconfigure(0,weight=2)
        self.patternTitle.columnconfigure(1,weight=1)
        self.patternTitle.columnconfigure(2,weight=1)
        self.patternEntry = tk.Entry(self.patternTitle,textvariable=self.browser,width=25)
        self.patternButton = tk.Button(self.patternTitle,text="Mặc định",relief=tk.GROOVE)
        self.patternClear = tk.Button(self.patternTitle,text="Chọn",relief=tk.GROOVE)

        self.patternTitle.grid(row=2,column=0,padx=10,pady=10,sticky="ew",ipadx=10)
        self.patternEntry.grid(row=0,column=0,padx=10,pady=10,sticky="sew")
        self.patternButton.grid(row=0,column=1,padx=10,pady=10,sticky="sew")
        self.patternClear.grid(row=0,column=2,padx=10,pady=10,sticky="sew")


    def changeEngine(self,*args):
        return    
    def changeLocation(self,*args):
        config.set('main','location',str(self.location.get()))
        with codecs.open('config.ini', 'w','utf-8') as f:
            config.write(f)
            f.close()
class MenuPage(tk.Toplevel):
    def __init__(self, master =None):
        super().__init__(master = master)
        
        self.title("Cài đặt")
        self.geometry("700x600")
        global curMenu
        self.master = master
        self.protocol("WM_DELETE_WINDOW", self.close)

        self.frameL = tk.Frame(self,width=250,border=10,bg="Slategray1")
       
        self.frameR = tk.Frame(self,border=5,bg="whitesmoke")
        self.frameR.pack_propagate(0)
        curMenu = Genreral(self.frameR,self.master)
      
        #General menu
        self.frame1 = tk.Frame(self.frameL,width= 250,height=75,border=0,bg="SkyBlue1")
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
        w,h = int(config.get("main","width")),int(config.get("main","height"))
        self.master.setSize(w,h)
        # self.master.controller.overrideredirect(False)
        self.master.controller.overrideredirect(True)
        
        self.destroy()

    def exit(self,*args):
        
        if messagebox.askyesno("Xác nhận","Bạn có muốn đóng chương trình?"):
            self.master.quit()
            self.destroy()
        # messageWindow(self.master)

def messageWindow(master):
    win = tk.Toplevel()
    win.title('Xác nhận')
    message = "Bạn có muốn đóng chương trình?"
    tk.Label(win, text=message).pack()
    tk.Button(win, text='Có', command=master.quit).pack()
    tk.Button(win, text='Không', command=win.destroy).pack()