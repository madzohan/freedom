import PyChromeDevTools
import time
import json
import re
from nba_playbyplay1 import nba
from navigate import chrome
import os
import threading
import random

chrome_ov = PyChromeDevTools.ChromeInterface(port = 9222)
new_tab = chrome_ov.Target.createTarget(url="https://www.7788365365.com/?&cb=105812118651#/IP/")
targetID = new_tab["result"]["targetId"][1:-1]
print('targetID：' + targetID)
chrome_ov = PyChromeDevTools.ChromeInterface(port = 9222)  ##不能删，什么用来着
chrome_ov.connect_targetID(targetID)
chrome_ov.Network.enable()
chrome_ov.Page.enable()
chrome_ov.DOM.enable()
Date = str(time.localtime()[0]) +str(time.localtime()[1])+str(time.localtime()[2])
try:
    os.mkdir('gamepickle/' + Date + '/')
except:
    print('文件已存在')
chrome_ov.Page.reload()
messages =[]
chrome_ov.ws.settimeout(10)
#提取信息的正则表达式
Flag_OVPlay = True
OV_bb = re.compile(r'CT;FF=;ID=18.*?(?=CT;FF=;ID)')
OV_drop = re.compile(r'CT;FF=;ID=18.*?(?=CL;CD=)')
NA = re.compile(r'(?<=NA=).*?(?=;)')
CC = re.compile(r'(?<=CC=).*?(?=;)')
CP = re.compile(r'(?<=CP=)\w*?(?=;)')
ID = re.compile(r'(?<=ID=)\w*?(?=;)')
IT = re.compile(r'(?<=IT=)\w*?(?=;)')
EV = re.compile(r'EV;AU.+?OR=1;PX=;SU=\d;')
all ={}
while True:
    while True:
        message =chrome_ov.ws.recv()
        if 'webSocketFrameReceived' in message[:45]:
            message =json.loads(message)['params']['response']['payloadData']
            messages.append(message)
            if 'OVInPlay' in message[:10]:
                # Flag_OVPlay = False
                GamesBB = OV_bb.findall(message)
                try:
                    GamesBB[-1] = OV_drop.findall(GamesBB[-1])[0]
                except IndexError:
                    print('No basketball games now!!!!')

                Games = [EV.findall(m) for m in GamesBB]
                date = {}
                IDtoGame = {}
                # 分割每场比赛的信息
                for games in Games:
                    for game in games:
                        info = {}
                        na =NA.findall(game)[0]
                        try:
                            info['TeamAway'] = re.split(r' @ | vs | v ',na)[0]
                            info['TeamHome'] = re.split(r' @ | vs | v ',na)[1]
                        except IndexError:
                            break
                        info['League'] = CC.findall(game)[0]
                        info['GameID'] = ID.findall(game)[0]
                        info['GameIT'] = IT.findall(game)[0]
                        info['Game_NID'] = Date+info['TeamAway']+'@'+info['TeamHome']
                        date[info['Game_NID']] = {'info':info}
                break
    diff = date.keys() - all.keys()
    all =date
    if diff !=[]:
        for key in diff:
            print(date[key]['info']['Game_NID'])
            id = date[key]['info']['GameID']
            print('请求比赛页面'+date[key]['info']['TeamAway'])
            page = chrome(date[key]['info']['TeamAway'],date[key]['info']['TeamHome'],date[key]['info']['League'])
            page.basketball()
            game = nba(page.chrome)
            my_thread = threading.Thread(target= game.parse, args=(id,))
            my_thread.start()
    print('当前所有比赛页面都已打开')
    chrome_ov.Page.reload()
    time.sleep(random.randint(30, 60))







