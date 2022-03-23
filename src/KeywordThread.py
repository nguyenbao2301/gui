import threading 
import ctypes
from src._dtw import DTWloop

from configparser import ConfigParser
config = ConfigParser()
config.read('config.ini')

class KeywordThread(threading.Thread):
    def __init__(self,func):
        threading.Thread.__init__(self)
        self.func = func
    def run(self):
        try:
            # while True:
                # print("s: ",config.get('main','sensitivity'))
            DTWloop(self.func)
        finally:
            print('ended')

    def get_id(self):
 
        # returns id of the respective thread
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id
  
    def raise_exception(self):
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
              ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')