
import tkinter as tk

class ASRBubble(tk.Toplevel):
    def __init__(self, master =None,text = ""):
        super().__init__(master = master)
        self.master = master


        x = self.master.controller.winfo_x()
        y = self.master.controller.winfo_y()
        self.overrideredirect(True)
        # print(self.winfo_screenheight(),y)
        if x>=200:
            x = x-220
        else:
            x = x +150

        # if y>=200:
        #     y = y-200
        # else :
        #     y = y +150
        self.title("New Window")
        self.geometry("+%d+%d" % (x, y))
        self.frame = tk.Frame(self,width = 200,height=100,bg = "white", highlightbackground="blue", highlightthickness=1)
        self.frame.pack_propagate(0)
        self.frame.pack()        
        self.label = tk.Label(self.frame,text=text,wraplength = 160,justify="left")
        self.label.pack(fill='both',expand=True)
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.after(3000, lambda: self.close())


    def close(self,*args):
        self.destroy()
        return  

# def recognize(master,recognizer,microphone,idsf):
#     with microphone as source:
#             audio = recognizer.listen(source,phrase_time_limit = 5)
#             try:
#                 response = recognizer.recognize_google(audio,language="vi-VN")
#             except Exception:
#                 response = None
#         # print(response, globals.status)
#     if response != None:
#         text,intent,slots = idsf.predict(response.lower())
#         print(intent,text,slots)
#         process(intent,text,slots,master)
#         ASRBubble(master,text)
#             # processor.process(response.lower())
#     else:
#         ASRBubble(master,"Sorry, I didn't quite get that")     
