from urllib.request import urlopen
from urllib.parse import urlencode
import urllib
import xml.etree.ElementTree as ET
from tkinter import *
from tkinter import ttk
from enum import Enum
import smtplib
from email.mime.text import MIMEText
import telepot
import folium
import selenium.webdriver
import requests

my_token = "key"

bot = telepot.Bot(token = my_token)
bot.getMe()
mylists = []
saveitem = ""
class TextType(Enum):
    LostItem = 0
    LostDay = 1
    LostSpot = 2
    LostInfo = 3
    LostTakeId = 4
def getMaps(string):
    urlParams = {
        'address': string,
        'sensor': 'false',
        'language' : 'ko',
        'key' : 'key'
    }
    url = 'https://maps.google.com/maps/api/geocode/json?' + urllib.parse.urlencode(urlParams)
    response = requests.get(url)
    data = response.json()
    lat = 0
    lng = 0
    if data['status'] != 'ZERO_RESULTS':
        lat = data['results'][0]['geometry']['location']['lat']
        lng = data['results'][0]['geometry']['location']['lng']
    return lat,lng

def handle(msg):
    global bot
    count = 0

    content_type, chat_type, chat_id = telepot.glance(msg)
    if content_type != 'text':
        bot.sendMessage(chat_id, "텍스트만 보내새유")
        return
    bot.sendMessage(chat_id, msg['text'] + ' 정보에 대해 알려드릴게요. ')
    for i in range(0, len(mylists), 1):
         if mylists[i][TextType.LostItem.value].find(msg['text']) != -1:
            count += 1
            bot.sendMessage(chat_id, "분실 물건 : " + mylists[i][TextType.LostItem.value] + "    분실 날짜 : " + mylists[i][TextType.LostDay.value] + "  분실 장소 :  " + mylists[i][TextType.LostSpot.value])

    if count is 0:
        bot.sendMessage(chat_id, "찾는 내용이 없습니다.")


class MyTk:
    def __init__(self):
        self.root = Tk()
        self.root.title('분실물 찾기 서비스')
        self.root.geometry('600x800')
        self.mylist = Listbox(self.root, selectmode='extended')
        self.mylist.place(x=20, y=50, width=200, height=400)
        self.strings = StringVar()
        self.emailadd = StringVar()
        self.textbox = ttk.Entry(self.root, textvariable=self.strings)
        self.textbox.place(x=20, y=5, width=200)

        self.textbox2 = ttk.Entry(self.root, textvariable = self.emailadd)
        self.textbox2.place(x=20, y =470, width = 400)

        self.searchButton = Button(self.root, text ="검색", overrelief="solid", command=self.getList, repeatdelay=1000, repeatinterval=100)
        self.searchButton.place(x=230, y=5, width=50, height=20)

        self.sendButton = Button(self.root, text = "전송", overrelief = "solid", command=self.sendButtonAction)
        self.sendButton.place(x =480, y = 470, width = 50, height =20)

        self.clearButton = Button(self.root, text = "초기화", overrelief = "solid", command = self.clear)
        self.clearButton.place (x = 290, y = 5, width = 70, height = 20)
        self.Label1 = Label(self.root, text="", relief='solid')
        self.Label1.place(x=250, y=80, width=300, height=40)

        self.Label2 = Label(self.root, text="", relief='solid')
        self.Label2.place(x=250, y=150, width=300, height=40)

        self.Label3 = Label(self.root, text="", relief='solid')
        self.Label3.place(x=250, y=220, width=300, height=40)

        self.Label4 = Label(self.root, text="", relief='solid', wraplength = 300)
        self.Label4.place(x=250, y=300, width=300, height=150)

        self.Label5 = Label(self.root, text="", relief='solid')
        self.Label5.place(x=20, y=530, width=560, height=250)

        self.Label6 = Label(self.root, text="최근 0건 검색")
        self.Label6.place(x = 20, y = 30)

        self.Label7 = Label(self.root, text="", justify = 'center')
        self.Label7.place(x=150, y=510, width = 100, height = 20)

        self.mylist.bind("<Double-Button-1>", self.selection)

        self.allcount = self.getCount()
        self.end = self.allcount
        self.start = self.end - 401
        self.yIdx = 0
        self.plan = 10
        self.selectNum = 0
        self.allViewNum = 0
        self.savestring = ""

        staticText = Label(self.root, text="분실 날짜")
        staticText.place(x = 360, y = 60, width = 80, height = 20)

        staticText2 = Label(self.root, text="분실 물건")
        staticText2.place(x=360, y=130, width=80, height=20)

        staticText3 = Label(self.root, text="분실 장소")
        staticText3.place(x=360, y=200, width=80, height=20)

        staticText4 = Label(self.root, text="분실 정보")
        staticText4.place(x=360, y=280, width=80, height=20)

        staticText5 = Label(self.root, text = "이메일 전송")
        staticText5.place(x=20, y = 450, width=70, height=20)

        staticText6 = Label(self.root, text="분실물 수령 위치 : ")
        staticText6.place(x=20, y=510, width=110, height=20)

        self.s = smtplib.SMTP('smtp.gmail.com',587)
        self.s.starttls()
        self.s.login('eMail', 'passWord')
        self.msg = MIMEText('내용: 본문 내용 테스트')
        self.msg['Subject'] = '제목: 메일 보내기 테스트'
        bot.message_loop(handle)

        self.root.mainloop()
    def clear(self):
        self.end = self.allcount
        self.start = self.end - 201
        self.savestring =""
        self.mylist.delete(0, self.mylist.size())
        self.Label6.config(text="최근 0건 검색")
    def sendButtonAction(self):
        global mylists
        receive = self.textbox2.get()
        listargs = mylists[self.selectNum]

        msg = MIMEText('분실 날짜 : ' + listargs[TextType.LostDay.value] + '\n' + '분실 물건 :  ' + listargs[TextType.LostItem.value] + '\n' + '분실 장소 : ' + listargs[TextType.LostSpot.value] + '\n' + '분실 정보 : \n' + listargs[TextType.LostInfo.value])
        msg['Subject'] = "LostItem"

        self.s.sendmail("eMail", receive,msg.as_string())

        self.s.quit()

    def selection(self, event):
        global mylists
        global saveitem
        listargs = mylists[event.widget.curselection()[0]]
        self.selectNum = event.widget.curselection()[0]
        self.Label1.config(text = listargs[TextType.LostDay.value])
        self.Label2.config(text = listargs[TextType.LostItem.value])
        self.Label3.config(text=listargs[TextType.LostSpot.value])
        self.Label4.config(text=listargs[TextType.LostInfo.value])
        if saveitem != listargs[TextType.LostTakeId.value]:
            lat,lng = getMaps(listargs[TextType.LostTakeId.value])
            if lat != 0 and lng != 0:
                a = folium.Map(location=[lat,lng], zoom_start=15)
                folium.Marker([lat,lng]).add_to(a)
                a.save("save.html")
                self.driver = selenium.webdriver.PhantomJS('phantomjs')
                self.driver.set_window_size(500, 200)
                self.driver.get('save.html')
                self.driver.save_screenshot('screenshot.png')
                photo = PhotoImage(file="screenshot.png")
                self.Label5.config(image = photo)
                saveitem = listargs[TextType.LostTakeId.value]
                self.Label7.config(text = saveitem)
            else:
                self.Label5.config(text="회사 정보를 읽어올 수 없습니다.", image = None)
                self.Label7.config(text='')
        else:
            return

    def getCount(self):
        testCase = "http://openapi.seoul.go.kr:8088/key/xml/lostArticleInfo/1/1/"
        return int(ET.ElementTree(file=urllib.request.urlopen(testCase)).getroot().findtext('list_total_count'))
    def getList(self):
        url = "http://openapi.seoul.go.kr:8088/key/xml/lostArticleInfo/" + str(
            self.start) + "/" + str(self.end) + "/"
        tree = ET.ElementTree(file=urllib.request.urlopen(url))
        root = tree.getroot()

        if self.savestring != self.strings.get():
            self.savestring = self.strings.get()
            self.mylist.delete(0, self.mylist.size())
            self.allViewNum = 0
            self.end = self.allcount

        for a in root.findall('row'):
            condition = a.findtext('GET_NAME')

            if a.findtext('STATUS') == "수령" or condition.find("고객") != -1 or condition.find("연락") != -1 or condition.find(self.strings.get()) == -1:
                continue

            if len(mylists) <= self.yIdx:
                mylists.append([])

            mylists[self.yIdx].append(a.findtext('GET_NAME'))
            mylists[self.yIdx].append(a.findtext('REG_DATE'))
            mylists[self.yIdx].append(a.findtext('GET_GOOD'))
            mylists[self.yIdx].append(a.findtext('GET_THING').replace("<br>", "\n"))
            mylists[self.yIdx].append(a.findtext('TAKE_ID'))

            self.mylist.insert(self.yIdx, mylists[self.yIdx][TextType.LostItem.value])

            self.yIdx += 1
        self.allViewNum += self.end - self.start - 1
        self.Label6.config(text="최근 {0}건 검색".format(self.allViewNum))
        self.end = self.start
        self.start = self.end - 401
        self.plan += 10


ab = MyTk()

