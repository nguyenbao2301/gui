
import time
from serpapi import GoogleSearch
import webbrowser
from youtube_search import YoutubeSearch
from datetime import date, timedelta, datetime
from src.alarm import addAlarm
from src.ASRBubble import ASRBubble
from src.tts import TTS
from configparser import ConfigParser
config = ConfigParser()
config.read('config.ini',encoding='utf-8')

weekdays = {'thứ hai':0, 'thứ ba':1, 'thứ tư':2, 'thứ năm':3, 'thứ sáu':4, 'thứ bảy':5, 'chủ nhật':6,'thứ 2':0, 'thứ 3':1, 'thứ 4':2, 'thứ 5':3, 'thứ 6':4, 'thứ 7':5}
times = {'một':1,"hai":2,"ba":3,"bốn":4,"năm":5,"sáu":6,"bảy":7,"tám":8,'chín':9,"mười":10}
class Service():
    def __init__(self,master,*params):
        self.master = master
        self.params = params
    def onException(self):
        ASRBubble(self.master,"Xin lỗi, tôi không nghe rõ câu đó")  
        TTS().speak("Xin lỗi, tôi không nghe rõ câu đó")

class AlarmTimerService(Service):
    def parseTime(self,arr): 
        pod = ""
        h=0
        m=0
        s=0
        try:
            if "pod" in arr.keys():
                pod = arr["pod"]

            if "time" in arr.keys():
                if any(filter(lambda i: i in arr['time'] , ['nửa tiếng', 'nửa giờ'])):
                        h = 0
                        m =30
                elif any(filter(lambda i: i in arr['time'] , ['nửa đêm','nửa'])):
                        h  = 0
                        m = 0
                else:
                    time = arr['time'] #"hh:mm" or "X giờ" or "X" 
                    print("time: ",time)
                    if ':' not in time:
                        h = time.split()[0]
                        print("h:",h)
                        h = int(h) if h not in times.keys() else times[h]
                        # time = "{:0>2d}:00".format(h)
                    else:
                        temp_h =  time.split(':')[0] 
                        h = int(temp_h.split()[0])   
                        temp_m =  time.split(':')[1]
                        m = int(temp_m.split()[0])
                    if pod != "" and not(any([i in pod for i in ['sáng','sớm','trưa']])):
                        # time = time.split(":")
                        # h = int(time[0])
                        # m= int(time[1])
                        if(h<=12):
                            h = h +12
                        # time ="{:0>2d}:{:0>2d}".format(h,time[1])
                        # time = str(h) +":"+ time[1]
                # print(time)
                # if h > 24  or (h==24 and m>0 ):
                #         return "",h,m,s
                # else: 
                #         return time+":00",h,m,ｓ
            if 'hour' in arr.keys():
                    if any(filter(lambda i: i in arr['hour'] , ['nửa tiếng','nửa giờ'])):
                        h = 0
                        m =30
                    elif any(filter(lambda i: i in arr['hour'] , ['nửa đêm','nửa'])):
                        h  = 0
                        m = 0

                    else:
                        temp = arr['hour'].split()[0] 
                        h = int(temp if temp not in times.keys() else times[temp])  
            if 'minute' in arr.keys():
                    if any(filter(lambda i: i in arr['minute'] ,['nửa','rưỡi'])):
                        m = 30
                    else:
                        temp = arr['minute'].split()[0] 
                        m = int(temp if temp not in times.keys() else times[temp])  
            if 'second' in arr.keys():
                    temp = arr['second'].split()[0] 
                    s = int(temp if temp not in times.keys() else times[temp])  
            print(h,m,s)

            print("R:","{:0>2d}:{:0>2d}:{:0>2d}".format(h,m,s))
            if h > 24 or (h==24 and (m>0 or s>0) ):
                    return "",h,m,s
            else: 
                    return "{:0>2d}:{:0>2d}:{:0>2d}".format(h,m,s),h,m,s
        except Exception:
                    return "",h,m,s    
    def parseDate(self,arr,_time): #return day  in dd/mm , "" if day couldnt be parsed
        try:
            repeat = False 
            today = date.today() #calculate if _time is has already passed today
            dt = datetime.combine(today, datetime.strptime(_time, '%H:%M:%S').time())

            _delta = datetime.now() < dt

            print("delta:",_delta)
            if _delta == True: #_time has not passed-> set alarm today
                day = today.strftime("%d/%m")
                print("\nday:",today.strftime("%d/%m"))
            else: #else set alarm tomorrow
                tmr = today + timedelta(days=1)
                day = tmr.strftime("%d/%m")
                print("\nday:",tmr)
            if "repeat" in arr.keys():
                repeat = True

            if 'date_name' in arr.keys():
                day = arr['date_name']
                if repeat:
                    return str(weekdays[day]) 
                if 'relative' in arr.keys():
                    day = WeekdayToDate(day,arr['relative'])
                else:
                    day = WeekdayToDate(day)
            elif 'date_number' in arr.keys():
                day = arr['date_number']
                if 'month' in arr.keys():
                    day = day + ' ' + arr['month']
                else: #no month provided
                    today = date.today()
                    month = today.strftime("%m")
                    day = day + " tháng " + str(month)
            elif 'relative' in arr.keys():
                    day = arr['relative']
                    day= formatDate(day)

            elif repeat:
                return 'X'

            day =day.replace('ngày ','').replace(' tháng ','/')
            while ('/' in day) and len(day) < 5: #pad to correct dd/mm format
                if day[1] == '/': #d/mm or d/m
                    day = '0' + day
                else:
                    day = day[:-1] + '0' + day[-1]
            
            return day
        except Exception:
            return ""
    def setAlarm(self):
        try:
            arr = self.params[0]
            _time,_,_,_ = self.parseTime(arr)
            print("time:",_time)
            day = self.parseDate(arr,_time)

            
            #cut seconds
            _time = _time[:-3]
            if _time == "" or day == "": #no time or date given
                print("Invalid")
                ASRBubble(self.master,"Xin lỗi, tôi không nghe rõ câu đó")  
                TTS().speak("Xin lỗi, tôi không nghe rõ câu đó")  
                return

            if day == "X":
                _date = "mỗi ngày"
                print("time: ",_time,"date: everyday")
            elif len(day) == 1:
                _date = arr['date_name']
                print("time: ",_time,"date: ",arr['date_name'])
            elif "/" in day:
                _date = "{}".format(day)
                print("time: ",_time,"date: ",day)
            ASRBubble(self.master,"Tôi đã đặt một báo thức lúc {} ngày {}".format(_time, _date),5000)
            TTS().speak("Tôi đã đặt một báo thức lúc {} ngày {}".format(_time, _date))
            addAlarm(day,_time)
        except Exception:
            self.onException()


    def setTimer(self,target): #target: MainApp frame
        try:
            arr = self.params[0]
            _time,h,m,s = self.parseTime(arr)
            if _time == "": #no time given
                print("Invalid")
                ASRBubble(self.master,"Xin lỗi, tôi không nghe rõ câu đó")  
                TTS().speak("Xin lỗi, tôi không nghe rõ câu đó")  
                return
            ASRBubble(self.master,"Tôi đã đặt một hẹn giờ cho {} giờ {} phút và {} giây".format(h,m,s),5000)  
            TTS().speak("Tôi đã đặt một hẹn giờ cho {} giờ {} phút và {} giây".format(h,m,s)) 
            target.setTimer(_time)
        except Exception:
            self.onException()
class MusicService(Service):
    def createQuery(self):
        try:
            arr = self.params[0]
            text = self.params[1]
            song_name = ""
            album = ""
            artist = ""
            genre = ""
            if "song_name" in arr.keys():
                song_name = "bài hát "+ arr["song_name"] 
            if "album" in arr.keys():
                album = "album" + arr['album']
            if "artist" in arr.keys():
                artist = arr['artist']
            if "genre" in arr.keys():
                genre = "nhạc " + arr['genre']

            if song_name != "" :
                query = song_name 
            elif album != "":
                query = "album "+ album 
            elif genre != "":
                query = genre 
            else:
                query = ""
            if artist != "":
                if query != "":
                    query = query + " của " + artist
                else:
                    query = artist
            
            if query == "":
                query = "nhạc"
            print("query: ",query)
            ASRBubble(self.master,"Đang mở "+ query)
            TTS().speak("Đang mở "+ query)
            return query
        except Exception:
            self.onException()
            return ""
    def searchQuery(self,query):
        if query == "":
            return
        while True:
            result = YoutubeSearch(query, max_results=10).to_dict()
            if result:
                break

        url = 'https://www.youtube.com' + result[0]['url_suffix']
        return url



    def play(self,url):
        if url == "":
            return
        try:
            webbrowser.open(url)
        except Exception:
                    print("Exception: "+str(Exception))

class WeatherService(Service):
    def parseDate(self,arr): #return day  in dd/mm , "" if day couldnt be parsed
        try:

            today = date.today() #calculate if _time is has already passed today
            
            day = today.strftime("%d/%m")

            if 'date_name' in arr.keys():
                day = arr['date_name']
                if 'relative' in arr.keys():
                    day = WeekdayToDate(day,arr['relative'])
                else:
                    day = WeekdayToDate(day)
            elif 'date_number' in arr.keys():
                day = arr['date_number']
                if 'month' in arr.keys():
                    day = day + ' ' + arr['month']
                else: #no month provided
                    today = date.today()
                    month = today.strftime("%m")
                    day = day + " tháng " + str(month)
            elif 'relative' in arr.keys():
                    day = arr['relative']
                    day= formatDate(day)

            day =day.replace('ngày ','').replace(' tháng ','/')
            while ('/' in day) and len(day) < 5: #pad to correct dd/mm format
                if day[1] == '/': #d/mm or d/m
                    day = '0' + day
                else:
                    day = day[:-1] + '0' + day[-1]
            
            return day
        except Exception:
            return ""
    def createQuery(self):
        try:
            arr = self.params[0]
            location = config.get("main","location")
            day = self.parseDate(arr)
            pod = ""


            if "location" in arr.keys():
                location = arr["location"]
            if "pod" in arr.keys():
                pod = arr["pod"]

            query = "thời tiết {} {} {}".format(location,pod,day) 
            print("query: ",query)
            return query
        except Exception:
            return "" 
    def searchQuery(self,query):
            search(query)


class SearchService(Service):
    def search(self,text):
        search(text)





def search(text):
            config.read('config.ini',encoding='utf-8')
            print("Query: ",text)
            # return
            tts = TTS()
            params = {
                "engine": "google",
                "q": text,
                "hl": "vi",
                # "location": config.get('main','location'),
                "gl": "vn",
                "device":"desktop",
                # "google_domain":"google.com.vn",
                "api_key": "ac1585c4813011483eff458315995105014d4f28d6a92ab4f9b0aefc1eb74ef2"
            }

            search = GoogleSearch(params)
            results = search.get_dict()
            
            try:
                webbrowser.open(results['search_metadata']['google_url'])
            except Exception:
                    print("Exception: "+str(Exception))
            
            knowledge_graph = None
            answer_box = None

            answer_box = None
            tts.speak("Đây là những gì tôi tìm được.")
            print(results)
            # time.sleep(1.5)
            if "knowledge_graph" in results.keys():
                knowledge_graph = results["knowledge_graph"] 
                print(knowledge_graph)
                desc = knowledge_graph["description"]
                tts.speak(desc)
                return
            elif 'answer_box' in results.keys():
                answer_box = results['answer_box']
            elif 'answer_box_list' in results.keys():
                answer_box = results['answer_box_list'][0]

            if answer_box:
                type = answer_box['type']
                if type == 'weather_result':
                    temp = answer_box['temperature']
                    location = answer_box['location']
                    day = answer_box['date']
                    weather = answer_box['weather']
                    humid = answer_box['humidity']
                    tts.speak("{} ngày {} {}, nhiệt độ {}, độ ẩm {}".format(location,day,weather,temp,humid))
                if type == "calculator_result":
                    res = answer_box['result']
                    tts.speak(res)
                if type == "population_result":
                    pop = answer_box["population"]
                    place = answer_box['place']
                    year = answer_box['year']

                    tts.speak("Dân số {} năm {} là {}.".format(place,year,pop))
                if type == "currency_converter":
                    res = answer_box['result']
                    tts.speak(res)
                if type == "dictionary_results":
                    defi = answer_box["dictionary_results"] #array of str
                    exs = answer_box["examples"] #array of str

                    tts.speak("{}. Ví dụ: {}".format(defi,exs))

                if type == "organic_result":
                    if 'snippet' in answer_box.keys():
                        res = answer_box["snippet"]
                    # if 'link' in answer_box.keys():
                    #     res = answer_box["link"] #array
                    # elif 'snippet' in answer_box.keys():
                    #     res = list(answer_box["snippet"]) #array
                        tts.speak(res)
                if type == 'translation_result':
                    res = answer_box["translation"]["target"]["text"]
                    tts.speak(res)
            else: 
                pass
            


def openLink(text):
        query = text.split()
        base_url = "https://www.google.com.vn/search?q="
        for word in query:
            base_url = base_url + word + "+"



        
def WeekdayToDate(day,relative = ""):
    today = date.today().weekday() #mon = 0, sun =6

    weekday = weekdays[day]
    if weekday - today <0:
        relative = "tuần sau"
    

    if relative not in ['này' , 'tuần này','']:
        offset = weekday + 7 - today
    else:
        offset = weekday - today    

    new_date = datetime.now() + timedelta(days = offset)
    new_date = new_date.strftime("%d/%m")
    print(new_date)
    return new_date
def formatDate(day):
    new_date = ""
    if day in ['hôm nay','nay']:
        new_date = date.today()
    elif day in ['mai','ngày mai','hôm sau','ngày hôm sau']:
        new_date = datetime.now() + timedelta(days = 1)
    elif day in ['mốt','ngày mốt','hôm sau nữa','ngày hôm sau nữa','2 ngày nữa']:
        new_date = datetime.now() + timedelta(days = 2)  
    elif 'ngày' in day and 'tháng' in day:
        temp = day.split() #ngày, X , tháng, Y
        d,m = temp[1], temp[3]
        print(d,m)
        return "{}/{}".format(d,m)
    elif any([i in day for i in ['ngày nữa','hôm nữa','ngày sau',' hôm sau']]):
        temp = day.split() #X ngày nữa
        offset = int(temp[0])
        new_date = datetime.now() + timedelta(days = offset)
    new_date = new_date.strftime("%d/%m") if new_date!= "" else day
    print(new_date)
    return new_date

# process("play_song",("mở giúp một ca khúc nào đó trong album vì lỡ thương nhau của ban nhạc tiết duy hòa và ca sĩ thùy trang","O O O O O O O O O B-album I-album I-album I-album O O O B-artist I-artist I-artist O O O B-artist I-artist"))