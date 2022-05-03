from playsound import playsound
from tkinter import font as tkfont
import time
from datetime import datetime
import tkinter as tk              
from src.keyword_recording import record_one, validate
import os

from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')

class RecordPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        audio_queue = []
        self.controller = controller
        global config

        

        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(2, weight=1)
        self.font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")
        self.frame = tk.Frame(self,height = 360,bg = "white")
        self.frame.pack_propagate(0)
        self.label = tk.Label(self.frame,text="Nhấn Ghi để bắt đầu",bg = "SkyBlue1",font = self.font)

        self.recordButton = tk.Button(self,text = "Ghi {}/3".format(1),command= lambda: self.record_keyword(1,audio_queue),relief=tk.GROOVE)
        self.nextButton = tk.Button(self, text="Tiếp tục",
                           command=lambda: controller.show_frame("TestingPage"),state="disabled",relief=tk.GROOVE)
        
        
        self.frame.grid(row=0,columnspan=3,sticky="new")
        self.label.pack(side = "top",fill="both",expand = True,padx=5,pady=5)
        self.recordButton.grid(row = 1,column=0,padx=5,sticky = "sew",pady=5)
        #self.listenButton.grid(row = 1,column=1,sticky="se",pady=5)
        self.nextButton.grid(row=1,column=2,padx=5,sticky="sew",pady=5)

        clearTemp("temp")
        tk.messagebox.showinfo(title = "Thêm từ khóa mới",message = "Để sử dụng chương trình, trước hết bạn cần đặt một từ khóa.\nBạn có thể chọn bất kì từ khóa nào mình thích.\nĐể thêm từ khóa mới, nhấn nút Ghi và nói từ khóa của bạn 3 lần.")

    def record_keyword(self,index,queue):
        controller = self.controller
        success = False
        global config
        directory = config.get('main','temp_dir')
        final_dir = config.get('main','pattern_dir')

        #update label
        self.label.config(bg="lime green",text="Đang ghi âm ...",fg="white")
        self.label.update()
        self.recordButton.config(state=tk.DISABLED)
        self.recordButton.update()

        if(index ==1):
            clearTemp("temp")
        #record and evaluate
        audio = record_one(directory,index)  
        status = validate(index,queue)
        if(status == 0 ): #valid record
            self.label.config(bg="SkyBlue1",text="Ghi âm thành công ({}/3)".format(index),fg="black")
            self.label.update()
            

            if index<3:
                
                # recordButton = tk.Button(frame,text = "Ghi {}/3".format(index+1),command=lambda: record_keyword(frame,index+1,queue,label))
                # recordButton.grid(row = 1,column=0,sticky='e')
                self.recordButton.config(text = "Ghi {}/3".format(index+1),command=lambda: self.record_keyword(index+1,queue))
                time.sleep(1)
                self.label.config(bg="SkyBlue1",text="Nhấn Ghi để bắt đầu",fg="white")
                self.label.update()
            else:
                time.sleep(1)
                self.label.config(bg="SkyBlue1",text="Ghi âm hoàn tất\nVui lòng nhấn Tiếp tục".format(index))
                self.label.update()
                for i, audio in enumerate(queue):
                    dest_path = os.path.join(final_dir, "{}.wav".format(datetime.now().timestamp()))
                    audio.write(dest_path)
                #unlock next
                self.nextButton.config(state=tk.NORMAL)
                self.nextButton.update()
                
                self.recordButton.config(text = "Ghi {}/3".format(index),command=lambda: self.record_keyword(index,queue))
                self.recordButton.update()

        elif(status == 1): #all invalid, reset
            self.label.config(bg="tomato3",text="Các bản ghi âm quá khác nhau\nVui lòng thử lại",fg="white")
            self.label.update()
            queue = []
            self.recordButton.config(text = "Ghi {}/3".format(1),command=self.record_keyword(1,queue))
            self.recordButton.update()

            time.sleep(1)
            self.label.config(bg="SkyBlue1",text="Nhấn Ghi để bắt đầu",fg="black")
            self.label.update()
            
            
        else: #invalid record
            self.label.config(bg="tomato3",text="Có quá nhiều tiếng ồn\nVui lòng thử lại.",fg="white")
            self.label.update()
            self.recordButton.config(text = "Ghi {}/3".format(index),command=lambda: self.record_keyword(index,queue))
            self.recordButton.update()

            time.sleep(1)
            self.label.config(bg="SkyBlue1",text="Nhấn Ghi để bắt đầu",fg="black")
            self.label.update()

        self.recordButton.config(state=tk.NORMAL)
        self.recordButton.update()            

    def on_switch(self):
        return

class RecordToplevel(tk.Toplevel):
    def __init__(self, master =None):
        super().__init__(master = master)
        # print("B")
        self.title("Ghi âm từ khóa mới")
        self.geometry("400x400")
        self.master = master
        self.protocol("WM_DELETE_WINDOW", self.close)

        audio_queue = []
        global config
        self.grid_columnconfigure(0, weight=1)
        
        

        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(2, weight=1)
        self.font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")
        self.frame = tk.Frame(self,height = 360,bg = "white")
        self.frame.pack_propagate(0)
        self.label = tk.Label(self.frame,text="Nhấn Ghi để bắt đầu",bg = "SkyBlue1",font = self.font)

        self.recordButton = tk.Button(self,text = "Ghi {}/3".format(1),command= lambda: self.record_keyword(1,audio_queue),relief=tk.GROOVE)
        self.nextButton = tk.Button(self, text="Hoàn thành",
                           command=lambda: self.close(),state="disabled",relief=tk.GROOVE)
        
        
        self.frame.grid(row=0,columnspan=3,sticky="new")
        self.label.pack(side = "top",fill="both",expand = True,padx=5,pady=5)
        self.recordButton.grid(row = 1,column=0,padx=5,sticky = "sew",pady=5)
        #self.listenButton.grid(row = 1,column=1,sticky="se",pady=5)
        self.nextButton.grid(row=1,column=2,padx=5,sticky="sew",pady=5)
        tk.messagebox.showinfo(title = "Thêm từ khóa mới",message = "Để thêm từ khóa mới, nhấn nút Ghi và nói từ khóa của bạn 3 lần.\nBạn có thể chọn bất kì từ khóa nào mình thích.")
        clearTemp("temp")

    def close(self,*args):
        print("closing")
        self.master.menu_opened = False
        self.destroy()

    def record_keyword(self,index,queue):
        fin = False
        global config
        directory = config.get('main','temp_dir')
        final_dir = config.get('main','pattern_dir')

        #update label
        self.label.config(bg="lime green",text="Đang ghi âm ...",fg="white")
        self.label.update()
        self.recordButton.config(state=tk.DISABLED)
        self.recordButton.update()

        if(index ==1):
            clearTemp("temp")
        #record and evaluate
        audio = record_one(directory,index)  
        status = validate(index,queue)
        if(status == 0 ): #valid record
            self.label.config(bg="SkyBlue1",text="Ghi âm thành công ({}/3)".format(index),fg="black")
            self.label.update()
            

            if index<3:
                
                # recordButton = tk.Button(frame,text = "Ghi {}/3".format(index+1),command=lambda: record_keyword(frame,index+1,queue,label))
                # recordButton.grid(row = 1,column=0,sticky='e')
                self.recordButton.config(text = "Ghi {}/3".format(index+1),command=lambda: self.record_keyword(index+1,queue))
                time.sleep(1)
                self.label.config(bg="SkyBlue1",text="Nhấn Ghi để bắt đầu",fg="white")
                self.label.update()
            else:
                time.sleep(1)
                self.label.config(bg="SkyBlue1",text="Ghi âm hoàn tất\nNhấn Hoàn thành để đóng".format(index))
                self.label.update()
                for i, audio in enumerate(queue):
                    dest_path = os.path.join(final_dir, "{}.wav".format(datetime.now().timestamp()))
                    audio.write(dest_path)
                #unlock next
                self.nextButton.config(state=tk.NORMAL)
                self.nextButton.update()
                
                self.recordButton.config(state= tk.DISABLED)
                self.recordButton.update()

        elif(status == 1): #all invalid, reset
            self.label.config(bg="tomato3",text="Các bản ghi âm quá khác nhau\nVui lòng thử lại",fg="white")
            self.label.update()
            queue = []
            self.recordButton.config(text = "Ghi {}/3".format(1),command=self.record_keyword(1,queue))
            self.recordButton.update()

            time.sleep(1)
            self.label.config(bg="SkyBlue1",text="Nhấn Ghi để bắt đầu",fg="black")
            self.label.update()
            
            
        else: #invalid record
            self.label.config(bg="tomato3",text="Có quá nhiều tiếng ồn\nVui lòng thử lại.",fg="white")
            self.label.update()
            self.recordButton.config(text = "Ghi {}/3".format(index),command=lambda: self.record_keyword(index,queue))
            self.recordButton.update()

            time.sleep(1)
            self.label.config(bg="SkyBlue1",text="Nhấn Ghi để bắt đầu",fg="black")
            self.label.update()

        self.recordButton.config(state=tk.NORMAL)
        self.recordButton.update()    
        
        return

    def listen(self):
        directory = config.get('main','temp_dir')
        dir = os.listdir(directory)
        p = path = os.path.join(directory,"wakeword_temp.wav")
        m = min(4,len(dir))
        if os.path.exists(p):
            m = m -1
        if m == 0:
            self.label.config(bg="tomato3",text="Nothing to play. Record something first.")
            self.label.update()
            return
        for i in range(m):
            self.label.config(bg="yellow2",text="Playing back ({}/{})".format(i+1,m))
            self.label.update()
            path = os.path.join(directory,"{0}.wav".format(i+1))
            if(os.path.exists(path)):
                playsound(path)
            time.sleep(0.5)
        
        time.sleep(1)
        self.label.config(bg="SkyBlue1",text="Nhấn Ghi để bắt đầu")
        self.label.update()
        return
    def on_switch(self):
        return
def clearTemp(directory):
    #empty temp directory
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e)) 