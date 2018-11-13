import PyChromeDevTools
import time
import json
import re
import pickle


from selenium.webdriver import Chrome,ChromeOptions

driver_path =  "D:/code/chromedriver.exe"  #chromedriver 路径
broswer_path =  "C:/Users/Administrator/AppData/Local/Google/Chrome/Application/chrome.exe"  #浏览器exe路径
Options = ChromeOptions()
Options.binary_location = broswer_path  #浏览器路径，不指定的话会自动查找Chrome 路径，如果Chrome安装的话
driver = Chrome(chrome_options=Options, executable_path = driver_path,port=9222)  #启动chromedriver，根据浏览器路径启动浏览器
driver.get( "https://www.365-777.com/#/IP/")

chrome = PyChromeDevTools.ChromeInterface()
chrome.Network.enable()
chrome.Page.enable()

Date = str(time.localtime()[0]) +str(time.localtime()[1])+str(time.localtime()[2])
# chrome.Page.navigate(url="https://www.365-777.com/#/IP/")
start=time.clock()
messages =[]
chrome.ws.settimeout(10)
Flag_OVPlay = True
OV_bb = re.compile(r'CT;FF=;ID=18.*?(?=CT;FF=;ID)')
OV_drop = re.compile(r'CT;FF=;ID=18.*?(?=CL;CD=)')
NA = re.compile(r'(?<=NA=).*?(?=;)')
CC = re.compile(r'(?<=CC=).*?(?=;)')
CP = re.compile(r'(?<=CP=)\w*?(?=;)')
ID = re.compile(r'(?<=ID=)\w*?(?=;)')
IT = re.compile(r'(?<=IT=)\w*?(?=;)')
SS = re.compile(r'(?<=SS=).*?(?=;)')
TM = re.compile(r'(?<=TM=).*?(?=;)')
TS = re.compile(r'(?<=TS=).*?(?=;)')
TU = re.compile(r'(?<=TU=).*?(?=;)')
HA = re.compile(r'(?<=HA=).*?(?=;)')
OD = re.compile(r'(?<=OD=).*?(?=;)')
FI = re.compile(r'(?<=HA=).*?(?=;)')
EV = re.compile(r'EV;AU.+?OR=1;PX=;SU=\d;')
x15x01 = re.compile(r'(?<=\x15).*?(?=\x01)')
BAR = re.compile(r'(?<=\|).+(?=\|)')

# messages = pickle.load(open('messages.pkl','rb'))
while True:
    try:
        message =chrome.ws.recv()
        #messages.append(json.loads(message))
        if 'webSocketFrameReceived' in message[:45]:
            message =json.loads(message)['params']['response']['payloadData']
            messages.append(message)


            while Flag_OVPlay:
                if 'OVInPlay' in message[:10]:
                    # Flag_OVPlay = False
                    GamesBB = OV_bb.findall(message)
                    GamesBB[-1] = OV_drop.findall(GamesBB[-1])[0]
                    Games = [EV.findall(m) for m in GamesBB]  # 分割每场比赛的信息
                    game = Games[0]
                    date = {}
                    IDtoGame = {}
                    for game in Games:
                        GM = [x.split('|') for x in game]
                        info ={}
                        data ={'CP':[],'SCA':[],'SCH':[],'TM':[],'TS':[],'LineSA':[],'LineSH':[]}
                        for gm in GM:
                            try:
                                info['TeamAway'] = re.split(r'@|vs',NA.findall(gm[0])[0])[0].replace(' ','')
                                info['TeamHome'] = re.split(r'@|vs',NA.findall(gm[0])[0])[1].replace(' ','')
                            except IndexError:
                                break
                            info['League'] = CC.findall(gm[0])[0]
                            data['CP'].append(CP.findall(gm[0])[0])
                            info['GameID'] = ID.findall(gm[0])[0]
                            info['GameIT'] = IT.findall(gm[0])[0]
                            data['SCA'].append( SS.findall(gm[0])[0].split('-')[0])
                            data['SCH'].append(SS.findall(gm[0])[0].split('-')[1])
                            data['TM'].append(TM.findall(gm[0])[0])
                            data['TS'].append(TS.findall(gm[0])[0])
                            data['LineSA'].append(HA.findall(gm[2])[0])
                            info['lineSA_ID'] = ID.findall(gm[2])[0]
                            info['lineSA_Team'] = NA.findall(gm[2])[0].split()[0]
                            data['LineSH'].append(NA.findall(gm[3])[0])
                            info['LineSH_ID'] = ID.findall(gm[3])[0]
                            info['LineSH_Team'] = NA.findall(gm[3])[0].split()[0]
                            info['GameDT_ID'] = Date+info['TeamAway']+'@'+info['TeamHome']
                            date[info['GameDT_ID']] = {'info':info,'data':data}
                            IDtoGame[info['lineSA_ID']] = info['GameDT_ID']
                            IDtoGame[info['LineSH_ID']] = info['GameDT_ID']
                            IDtoGame[info['GameID']] = info['GameDT_ID']
                            IDtoGame[info['GameIT']] = info['GameDT_ID']
                    def togame(x):
                        return IDtoGame.get(x,0)
                break
                break

            if message[0] == '\x15':
                for m in message.split('\x08'):
                    try:
                        GameDT_ID = togame(x15x01.findall(m)[0])
                        duplicate = []
                        if GameDT_ID != 0:
                            print(GameDT_ID,x15x01.findall(m)[0],message)
                            cells = BAR.findall(m)[0].split(';')
                            for cell in cells[:-1]:
                                c = cell.split('=')
                                if c[0] not in duplicate:
                                    duplicate.append(c[0])
                                    date[GameDT_ID]['data'][cells[0]].append(c[1])

                    except:
                        continue

    except:
        continue
    if len(messages) > 200:
        break

chrome.ws.settimeout(chrome.timeout)
for m in messages:
    print('\n', m)

pickle.dump(messages, open("messages.pkl", "wb"))

GameDT_ID = '20171218GombeBulls@KanoPillars'
