from calendar import week
from operator import add
from serpapi import GoogleSearch
import requests
import webbrowser
import json
from youtube_search import YoutubeSearch
from datetime import date, timedelta, datetime
from src.alarm import addAlarm
from src.ASRBubble import ASRBubble

from configparser import ConfigParser
config = ConfigParser()
config.read('config.ini')

weekdays = {'thứ hai':0, 'thứ ba':1, 'thứ tư':2, 'thứ năm':3, 'thứ sáu':4, 'thứ bảy':5, 'chủ nhật':6}

def recognize(master,recognizer,microphone,idsf):
    with microphone as source:
            audio = recognizer.listen(source,phrase_time_limit = 5)
            try:
                response = recognizer.recognize_google(audio,language="vi-VN")
            except Exception:
                response = None
        # print(response, globals.status)
    if response != None:
        text,intent,slots = idsf.predict(response.lower())
        print(intent,text,slots)
        process(intent,text,slots,master)
        ASRBubble(master,text)
            # processor.process(response.lower())
    else:
        ASRBubble(master,"Sorry, I didn't quite get that")     

def extract(text,labels):
    content = ""
    temp = ""
    arr = {}
    for word,label in zip(text.split(),labels):
        if label == "O":
            if content != "":
                arr[content] = temp[:-1]
            content = ""
            temp = ""
        elif label[0] == "B":
            if(label[2:] != content) and content != "":
                arr[content] = temp[:-1]
                temp = ""
            content = label[2:]
            print(content)
        if content != "":
            temp = temp + word + " "
    if content != "":
        arr[content] = temp[:-1]
    print(arr)
    return arr

def process(intent,text,slots,target = None):
    print(intent,text,slots)
    arr = extract(text,slots)
    if intent == "play_song":
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
            query = song_name + artist
        elif album != "":
            query = album + artist
        elif genre != "":
            query = genre + artist
        elif artist != "":
            query = "nhạc "+ artist
        else:
            query = text
        
        print("query: ",query)
        while True:
            result = YoutubeSearch(query, max_results=10).to_dict()
            if result:
                break

        url = 'https://www.youtube.com' + result[0]['url_suffix']
        try:
            webbrowser.open(url)
        except Exception:
                    print("Exception: "+str(Exception))


    elif intent == "alarm":
        today = date.today()
        day = today.strftime("%d/%m")
        day = getDate(arr,day)

        _time = getTime(arr)
        #cut seconds
        _time = _time[:-3]

        if _time == "": #no time given
            print("Invalid")
            return

        if day == "X":
            print("time: ",_time,"date: everyday")
        elif len(day) == 1:
            print("time: ",_time,"date: ",arr['date_name'])
        else:
            print("time: ",_time,"date: ",day)

        addAlarm(day,_time)

    elif intent == "timer":
        _time = getTime(arr)
        if _time == "": #no time given
            print("Invalid")
            return
        target.setTimer(_time)

    elif intent == "weather":
        location = config.get("main","location")
        today = date.today
        day = today.strftime("%d/%m")
        pod = ""
        date_name = ""

        if "location" in arr.keys():
            location = arr["location"]
        if "pod" in arr.keys():
            pod = arr["pod"]
        day = getDate(arr,day)

        query = "thời tiết {} {} {}".format(location,pod,day) 
        print("query: ",query)
        search()
    else:
        search(text)
    return

def search(text,intent = "None"):
            params = {
                "engine": "google",
                "q": text,
                "hl": "vi",
                "gl": "vn",
                "api_key": "8f895d4f9e14d48761d579bab1dcf57c47cd52209db5d5537ab1aeb88c3a61c0"
            }

            search = GoogleSearch(params)
            results = search.get_dict()

            knowledge_graph = None
            answer_box = None

            answer_box = None
            if "knowledge_graph" in results.keys():
                knowledge_graph = results["knowledge_graph"] 
                # print(type(knowledge_graph), knowledge_graph)
                desc = knowledge_graph["description"]
                print(desc)
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
                    print(location,day,weather,temp,humid)
                if type == "calculator_result":
                    res = answer_box['result']
                    print(res)
                if type == "population_result":
                    pop = answer_box["population"]
                    place = answer_box['place']
                    year = answer_box['year']

                    print(place,pop,year)
                if type == "currency_converter":
                    res = answer_box['result']
                    print(res)
                if type == "dictionary_results":
                    defi = answer_box["dictionary_results"] #array of str
                    exs = answer_box["examples"] #array of str

                    print(defi,exs)

                if type == "organic_result":
                    if 'link' in answer_box.keys():
                        res = answer_box["list"] #array
                    elif 'snippet' in answer_box.keys():
                        res = list(answer_box["snippet"]) #array
                    print(res)
                if type == 'translation_result':
                    res = answer_box["translation"]["target"]["text"]
                    print(res)
                openLink(text)


def openLink(text):
        query = text.split()
        base_url = "https://www.google.com/search?q="
        for word in query:
            base_url = base_url + word + "+"
        try:
            webbrowser.open(base_url)
        except Exception:
                    print("Exception: "+str(Exception))


def getDate(arr,day):  
    repeat = False
    if "repeat" in arr.keys():
        repeat = True

    if 'date_name' in arr.keys():
        day = arr['date_name']
        if repeat:
            return str(weekdays[day]) 
        if 'relative' in arr.keys():
            WeekdayToDate(day,arr['relative'])
        else:
            WeekdayToDate(day)
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
    return day

def getTime(arr):
    pod = ""
    if "pod" in arr.keys():
        pod = arr["pod"]

    if "time" in arr.keys():
        time = arr['time'] #"hh:mm" or "X giờ"
        if ':' not in time:
            time = time.split()[0] + ':00'
        if pod not in ["sáng", "trưa",""]:
            time = time.split(":")
            h = int(time[0])
            if(h<12):
                h = h +12
            time = str(h) +":"+ time[1]
        print(time)
        return time+":00"
    else:
        h=""
        m=""
        s=""
        if 'hour' in arr.keys():
            h = arr['hour'].split()[0]
        if 'minute' in arr.keys():
            m = arr['minute'].split()[0]
        if 'second' in arr.keys():
            s = arr['second'].split()[0]
        print(h,m,s)

        if h== "" and m == "" and s == "":
            return ""
        return "{}:{}:{}".format(h,m,s)
        
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
    else:
        temp = day.split() #X ngày nữa
        offset = int(temp[0])
        new_date = datetime.now() + timedelta(days = offset)
    new_date = new_date.strftime("%d/%m")
    print(new_date)
    return new_date

# process("play_song",("mở giúp một ca khúc nào đó trong album vì lỡ thương nhau của ban nhạc tiết duy hòa và ca sĩ thùy trang","O O O O O O O O O B-album I-album I-album I-album O O O B-artist I-artist I-artist O O O B-artist I-artist"))