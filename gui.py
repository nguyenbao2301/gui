
import tkinter as tk              
from tkinter import font as tkfont
import os



from src.TestingPage import TestingPage
from src.MainApp import MainApp
from src.MenuPage import MenuPage
from src.RecordPage import RecordPage

from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')

class SampleApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        self.geometry("400x400")
        self.minsize(400,400)
        self.maxsize(400,400)
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        self.curFrame = self.container
        self.frames = {
            "StartPage": StartPage, 
            "PageOne": PageOne, 
            "PageTwo": PageTwo,
            "RecordPage": RecordPage,
            "TestingPage": TestingPage,
            "MainApp": MainApp,
            "MenuPage": MenuPage,
            "FinishPage": FinishPage,
        }
        # for F in (StartPage, PageOne, PageTwo, RecordPage, TestingPage):
        #     page_name = F.__name__
        #     frame = F(parent=container, controller=self)
        #     self.frames[page_name] = frame

        #     # put all of the pages in the same location;
        #     # the one on the top of the stacking order
        #     # will be the one that is visible.
        #     frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MainApp")

    # def show_frame(self, page_name):
    def show_frame(self, page_name):
        # destroy the old frame
        if hasattr(self.curFrame,'on_switch'):
            self.curFrame.on_switch()
        for child in self.winfo_children():
            child.destroy()

        # create the new frame
        frame_class = self.frames[page_name]
        frame = frame_class(parent=self, controller=self)
        frame.pack(fill="both", expand=True)

class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="This is the start page", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)

        button1 = tk.Button(self, text="Go to Record Page",
                            command=lambda: controller.show_frame("PageOne"))
        button2 = tk.Button(self, text="Go to Sensitivity Test",
                            command=lambda: controller.show_frame("TestingPage"))
        button3 = tk.Button(self, text="Go to Main App",
                            command=lambda: controller.show_frame("MainApp"))
        button1.pack()
        button2.pack()
        button3.pack()

    def on_switch(self):
        return
class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Welcome", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        label2 = tk.Label(self,text = "We'll get you setup in just a few steps")
        label2.pack(fill="both",expand=True)
        button = tk.Button(self, text="Get started ",
                           command=lambda: controller.show_frame("RecordPage"))
        button.pack(side = "bottom",pady = 20)
    def on_switch(self):
        return
class FinishPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="All done", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        label2 = tk.Label(self,text = "The app is ready to use")
        label2.pack(fill="both",expand=True)
        button = tk.Button(self, text="Lets go",
                           command=lambda: controller.show_frame("MainApp"))
        button.pack()
    def on_switch(self):
        return

class PageTwo(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="This is page 2", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        button = tk.Button(self, text="Go to the start page",
                           command=lambda: controller.show_frame("StartPage"))
        button.pack()
    def on_switch(self):
        return


if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()