from playsound import playsound
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

        

        self.grid_columnconfigure(0, weight=1)
        
        self.frame = tk.Frame(self,height = 360,bg = "white")
        self.frame.pack_propagate(0)
        self.label = tk.Label(self.frame,text="Press Record to start",bg = "SkyBlue1")

        self.recordButton = tk.Button(self,text = "Record {}/3".format(1),command= lambda: self.record_keyword(1,audio_queue))
        self.listenButton = tk.Button(self, text="Listen back",command=self.listen,state="disabled")
        self.nextButton = tk.Button(self, text="Next",
                           command=lambda: controller.show_frame("TestingPage"),state="disabled")
        # button.pack()
        
        
        self.frame.grid(row=0,columnspan=3,sticky="new")
        self.label.pack(side = "top",fill="both",expand = True)
        self.recordButton.grid(row = 1,column=0,padx=5,sticky = "sew",pady=5)
        self.listenButton.grid(row = 1,column=1,sticky="se",pady=5)
        self.nextButton.grid(row=1,column=2,padx=5,sticky="se",pady=5)

        clearTemp("temp")
        tk.messagebox.showinfo(title = "Keyword setup",message = "You can use this program with any keyword you like.\nTo set up a keyword, record yourself saying it 3 times.")

    def record_keyword(self,index,queue):
        controller = self.controller
        success = False
        fin = False
        global config
        directory = config.get('main','temp_dir')
        final_dir = config.get('main','pattern_dir')

        #update label
        self.label.config(bg="lime green",text="Recording")
        self.label.update()


        if(index ==1):
            clearTemp("temp")
        #record and evaluate
        audio = record_one(directory,index)  
        status = validate(index,queue)
        if(status == 0 ): #valid record
            self.label.config(bg="SkyBlue1",text="Audio recorded successfully ({}/3)".format(index))
            self.label.update()
            

            if index<3:
                
                # recordButton = tk.Button(frame,text = "Record {}/3".format(index+1),command=lambda: record_keyword(frame,index+1,queue,label))
                # recordButton.grid(row = 1,column=0,sticky='e')
                self.recordButton.config(text = "Record {}/3".format(index+1),command=lambda: self.record_keyword(index+1,queue))
                time.sleep(1)
                self.label.config(bg="SkyBlue1",text="Press Record to start")
                self.label.update()
            else:
                time.sleep(1)
                self.label.config(bg="SkyBlue1",text="Press Next to continue.\nListen to hear playbacks.\nRecord to try again.".format(index))
                self.label.update()
                for i, audio in enumerate(queue):
                    dest_path = os.path.join(final_dir, "{}.wav".format(datetime.now().timestamp()))
                    audio.write(dest_path)
                #unlock next
                self.nextButton.config(state=tk.NORMAL)
                self.nextButton.update()
                
                self.recordButton.config(text = "Record {}/3".format(index),command=lambda: self.record_keyword(index,queue))
                self.recordButton.update()

        elif(status == 1): #all invalid, reset
            self.label.config(bg="tomato3",text="Audio records are inconsistent.\n Please try again.",fg="white")
            self.label.update()
            queue = []
            self.recordButton.config(text = "Record {}/3".format(1),command=self.record_keyword(1,queue))
            self.recordButton.update()

            time.sleep(1)
            self.label.config(bg="SkyBlue1",text="Press Record to start")
            self.label.update()
            
            
        else: #invalid record
            self.label.config(bg="tomato3",text="There's too much noise.\n Please try again.",fg="white")
            self.label.update()
            self.recordButton.config(text = "Record {}/3".format(index),command=lambda: self.record_keyword(index,queue))
            self.recordButton.update()

            time.sleep(1)
            self.label.config(bg="SkyBlue1",text="Press Record to start")
            self.label.update()

        #unlock listen 
        if(fin == False):
            self.listenButton.config(state=tk.NORMAL)
            self.listenButton.update()
            fin = True
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
        self.label.config(bg="SkyBlue1",text="Press Record to start")
        self.label.update()
        return
    def on_switch(self):
        return

class RecordToplevel(tk.Toplevel):
    def __init__(self, master =None):
        super().__init__(master = master)
        # print("B")
        self.title("Record Keyword")
        self.geometry("400x400")
        self.master = master
        self.protocol("WM_DELETE_WINDOW", self.close)

        audio_queue = []
        global config
        self.grid_columnconfigure(0, weight=1)
        
        self.frame = tk.Frame(self,height = 360,bg = "white")
        self.frame.pack_propagate(0)
        self.label = tk.Label(self.frame,text="Press Record to start",bg = "SkyBlue1")

        self.recordButton = tk.Button(self,text = "Record {}/3".format(1),command= lambda: self.record_keyword(1,audio_queue))
        self.listenButton = tk.Button(self, text="Listen back",command=self.listen,state="disabled")
        self.nextButton = tk.Button(self, text="Finish",
                           command=self.close,state="disabled")
        # button.pack()
        
        
        self.frame.grid(row=0,columnspan=3,sticky="new")
        self.label.pack(side = "top",fill="both",expand = True)
        self.recordButton.grid(row = 1,column=0,padx=5,sticky = "sew",pady=5)
        self.listenButton.grid(row = 1,column=1,sticky="se",pady=5)
        self.nextButton.grid(row=1,column=2,padx=5,sticky="se",pady=5)

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
        self.label.config(bg="lime green",text="Recording")
        self.label.update()


        if(index ==1):
            clearTemp("temp")
        #record and evaluate
        audio = record_one(directory,index)  
        status = validate(index,queue)
        if(status == 0 ): #valid record
            self.label.config(bg="SkyBlue1",text="Audio recorded successfully ({}/3)".format(index))
            self.label.update()
            
            if index<3:
                
                # recordButton = tk.Button(frame,text = "Record {}/3".format(index+1),command=lambda: record_keyword(frame,index+1,queue,label))
                # recordButton.grid(row = 1,column=0,sticky='e')
                self.recordButton.config(text = "Record {}/3".format(index+1),command=lambda: self.record_keyword(index+1,queue))
                time.sleep(1)
                self.label.config(bg="SkyBlue1",text="Press Record to start")
                self.label.update()
            else:
                time.sleep(1)
                self.label.config(bg="SkyBlue1",text="Press Next to continue.\nListen to hear playbacks.\nRecord to try again.".format(index))
                self.label.update()
                for i, audio in enumerate(queue):
                    dest_path = os.path.join(final_dir, "{}.wav".format(datetime.now().timestamp()))
                    audio.write(dest_path)
                #unlock next
                self.nextButton.config(state=tk.NORMAL)
                self.nextButton.update()
                
                self.recordButton.config(text = "Record {}/3".format(index),command=lambda: self.record_keyword(index,queue))
                self.recordButton.update()

        elif(status == 1): #all invalid, reset
            self.label.config(bg="tomato3",text="Audio records are inconsistent.\n Please try again.",fg="white")
            self.label.update()

            queue = []
            self.recordButton.config(text = "Record {}/3".format(1),command=self.record_keyword(1,queue))
            self.recordButton.update()

            time.sleep(1)
            self.label.config(bg="SkyBlue1",text="Press Record to start")
            self.label.update()
            
            
        else: #invalid record
            self.label.config(bg="tomato3",text="There's too much noise.\n Please try again.",fg="white")
            self.label.update()
            self.recordButton.config(text = "Record {}/3".format(index),command=lambda: self.record_keyword(index,queue))
            self.recordButton.update()

            time.sleep(1)
            self.label.config(bg="SkyBlue1",text="Press Record to start")
            self.label.update()
        #unlock listen 
        if(fin == False):
            self.listenButton.config(state=tk.NORMAL)
            self.listenButton.update()
            fin = True
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
        self.label.config(bg="SkyBlue1",text="Press Record to start")
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