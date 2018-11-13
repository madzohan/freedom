import PyChromeDevTools
import time
import json
import re
import pickle
import pandas as pd
import numpy as np

# chrome = PyChromeDevTools.ChromeInterface()
# chrome.Network.enable()
# chrome.Page.enable()
# chrome.Animation.enable()


# Date = str(time.localtime()[0])) +str(time.localtime()[1])+str(time.localtime()[2])
# chrome.Page.navigate(url="https://www.365-777.com/#/IP/")
# start=time.clock()
# messages =[]
# chrome.ws.settimeout(10)
#提取信息的正则表达式

Flag1 = True
OV_bb = re.compile(r'CT;FF=;ID=18.*?(?=CT;FF=;ID)')
OV_drop = re.compile(r'CT;FF=;ID=18.*?(?=CL;CD=)')
NA = re.compile(r'(?<=NA=).*?(?=;)')#name
CC = re.compile(r'(?<=CC=).*?(?=;)')#
CL = re.compile(r'(?<=CL=).*?(?=;)')
CT = re.compile(r'(?<=CT=).*?(?=;)')#league
CP = re.compile(r'(?<=CP=)\w*?(?=;)')#
ED = re.compile(r'(?<=ED=).*?(?=;)')# quarter
ID = re.compile(r'(?<=ID=)\w*?(?=;)')
IT = re.compile(r'(?<=IT=)\w*?(?=;)')
S1 = re.compile(r'(?<=S1=).*?(?=;)')
S2 = re.compile(r'(?<=S2=).*?(?=;)')
S3 = re.compile(r'(?<=S3=).*?(?=;)')
S4 = re.compile(r'(?<=S4=).*?(?=;)')
S5 = re.compile(r'(?<=S5=).*?(?=;)')
S6 = re.compile(r'(?<=S6=).*?(?=;)')
S7 = re.compile(r'(?<=S7=).*?(?=;)')
S8 = re.compile(r'(?<=S8=).*?(?=;)')
SC = re.compile(r'(?<=SC=).*?(?=;)')
SS = re.compile(r'(?<=SS=).*?(?=;)')
SU= re.compile(r'(?<=SU=).*?(?=;)')
TM = re.compile(r'(?<=TM=).*?(?=;)')#minute
TS = re.compile(r'(?<=TS=).*?(?=;)')#second
TU = re.compile(r'(?<=TU=).*?(?=;)')#time update
TT = re.compile(r'(?<=TT=).*?(?=;)')#time TICKING
TD = re.compile(r'(?<=TD=).*?(?=;)')#COUNTDOWN, TAX_DETAILS
HA = re.compile(r'(?<=HA=).*?(?=;)')#handicap
OD = re.compile(r'(?<=OD=).*?(?=;)')#odds
OR = re.compile(r'(?<=OR=).*?(?=;)')#order
FI = re.compile(r'(?<=HA=).*?(?=;)')
EV = re.compile(r'EV;AU.+?OR=1;PX=;SU=\d;')
VC = re.compile(r'(?<=VC=).*?(?=;)')

x15x01 = re.compile(r'(?<=\x15).*?(?=\x01)')
x14x01 = re.compile(r'(?<=\x14).*?(?=\x01)')
x15x08 = re.compile(r'(?<=\x15).*?(?=\x08)')
x08x01 = re.compile(r'(?<=\x08).*?(?=\x01)')
BAR = re.compile(r'(?<=\|).*?(?=\|)')
FlagGame = False
FlagQuarter = False
FlagHalf = False
FlagInterval = False
Flag1 = True
Flag2 = False
Flag3 = False
Flag_ADD = False
tail = '_10_0'
info = {}
check = []
full = {'ED': [], 'TM': [], 'TS': [], 'TU': [], 'TT': [], 'TD': [],'SU': []
    , 'S1_h': [], 'S2_h': [], 'S3_h': [], 'S4_h': [], 'S5_h': [], 'S6_h': [], 'SC_h': [], 'S1_a': [], 'S2_a': []
    , 'S3_a': [], 'S4_a': [], 'S5_a': [], 'S6_a': [],'SC_a': [],'HASH':[],'HASH_ODD':[],'HASA':[],'HASA_ODD':[]
    , 'HATU':[], 'HATU_ODD':[], 'HATD':[], 'HATD_ODD':[],'WH_ODD':[],'WA_ODD':[]}
rowNAN = pd.DataFrame(full)

half = {'HASH':[],'HASH_ODD':[],'HASA':[],'HASA_ODD':[]
    , 'HATU':[], 'HATU_ODD':[], 'HATD':[], 'HATD_ODD':[],'WH_ODD':[],'WA_ODD':[]}
quarter = {'quarter':[],'HASH':[],'HASH_ODD':[],'HASA':[],'HASA_ODD':[]
    , 'HATU':[], 'HATU_ODD':[], 'HATD':[], 'HATD_ODD':[],'WH_ODD':[],'WA_ODD':[]}
interval = {}
line = {}
ids = []
idKeys = ['GameIT','TeamHomeIT','TeamAwayIT','HASH_ID','HASA_ID','HATU_ID','HATD_ID','WH_ID','WA_ID']

def odd(x):
    return{'1/1':1,'3/4':0.75,'4/5':0.8,'4/6':0.66,'5/4': 1.25,'5/6':0.83,'5/8': 0.63,'5/11':0.45,'5/7':0.71,'5/9': 0.56,'6/4': 1.5,'6/7':0.86,'6/5':1.2,
           '7/4':1.75,'8/9':0.89,'10/11':0.91,'10/13':0.77,'10/21': 0.47,'11/10':1.1,'13/10': 1.3,'17/10': 1.7,'20/21':0.95,
           '20/23':0.87,'20/27':0.74,'20/29':0.69,'20/33': 0.61,'20/31':0.65,'21/20':1.05,'23/20':1.15,'27/20': 1.35}.get(x,0)
def keys(x,id,info):
    if id == info['TeamHomeIT']:
        return {'S1': 'S1_h','S2': 'S2_h','S3': 'S3_h','S4': 'S4_h','S5': 'S5_h','S6': 'S6_h','SC': 'SC_h'}.get(x, x)
    elif id == info['TeamAwayIT']:
        return {'S1': 'S1_a','S2': 'S2_a','S3': 'S3_a','S4': 'S4_a','S5': 'S5_a','S6': 'S6_a','SC': 'SC_a'}.get(x, x)
    elif id == info['HASH_ID']:
        return {'HA': 'HASH','OD': 'HASH_ODD'}.get(x, x)
    elif id == info['HASA_ID']:
        return {'HA': 'HASA','OD': 'HASA_ODD'}.get(x, x)
    elif id == info['HATU_ID']:
        return {'HA': 'HATU','OD': 'HATU_ODD'}.get(x, x)
    elif id == info['HATD_ID']:
        return {'HA': 'HATD','OD': 'HATD_ODD'}.get(x, x)
    elif id == info['WH_ID']:
        return {'OD': 'WH_ODD'}.get(x, x)
    elif id == info['WA_ID']:
        return {'OD': 'WA_ODD'}.get(x, x)
    else:
        return x

messages = pickle.load(open('messages0106.pkl','rb'))

for message in messages:
    while Flag1:
        if 'EV;C1=1' in message[:300] and 'CL=18' in message[:350]:
            Flag1 = False
            Flag2 = True
            cells = BAR.findall(message.split('\x01')[-1])
            # info['GameID'] = x14x01.findall(cells[0])[0]
            info['League'] = CT.findall(cells[0])[0]
            full['ED'].append(ED.findall(cells[0])[0])
            info['GameID'] = ID.findall(cells[0])[0]
            info['GameIT'] = IT.findall(cells[0])[0]
            na =NA.findall(cells[0])[0]
            info['TeamAway'] = re.split(r'@|v|vs',na)[1].strip()
            info['TeamHome'] = re.split(r'@|v|vs',na)[0].strip()
            # full['SC_a'].append(int( SS.findall(cells[0])[0].split('-')[1]))
            # full['SC_h'].append(int(SS.findall(cells[0])[0].split('-')[0]))
            full['TM'].append(int(TM.findall(cells[0])[0]))
            full['TS'].append(int(TS.findall(cells[0])[0]))
            full['TU'].append(TU.findall(cells[0])[0])
            full['TT'].append(TT.findall(cells[0])[0])
            full['TD'].append(TD.findall(cells[0])[0])
            full['SU'].append(0)

            info['TeamHomeIT'] = IT.findall(cells[2])[0]
            full['S1_h'].append(int(S1.findall(cells[2])[0]))
            full['S2_h'].append(int(S2.findall(cells[2])[0]))
            full['S3_h'].append(int(S3.findall(cells[2])[0]))
            full['S4_h'].append(int(S4.findall(cells[2])[0]))
            full['S5_h'].append(int(S5.findall(cells[2])[0]))
            full['S6_h'].append(float(S6.findall(cells[2])[0]))
            # full['S7_h'].append((S7.findall(cells[2])[0]))
            full['SC_h'].append(int(SC.findall(cells[2])[0]))
            info['TeamAwayIT'] = IT.findall(cells[3])[0]
            full['S1_a'].append(int(S1.findall(cells[3])[0]))
            full['S2_a'].append(int(S2.findall(cells[3])[0]))
            full['S3_a'].append(int(S3.findall(cells[3])[0]))
            full['S4_a'].append(int(S4.findall(cells[3])[0]))
            full['S5_a'].append(int(S5.findall(cells[3])[0]))
            full['S6_a'].append(float(S6.findall(cells[3])[0]))
            # full['S7_a'].append((S7.findall(cells[3])[0]))
            full['SC_a'].append(int(SC.findall(cells[3])[0]))
        break

    while Flag2:
        if  info['GameID'] in message[:30] and 'F|EV;' in message[:30]:
            Flag2 = False
            Flag3 = True
            cells = BAR.findall(message)
            for cell in cells:
                if 'MG;4Q' == cell[:5]:
                    na = NA.findall(cell)[0]
                    if na =='比赛投注':
                        FlagGame = True
                    # elif '节投注' in na:
                    #     FlagQuarter = True
                    elif na == '上半场投注':
                        FlagHalf = True
                    elif na == '输赢比数':
                        FlagInterval = True

                while FlagGame:
                    if 'MA;CN=1' == cell[:7]:
                        na = NA.findall(cell)[0]
                    elif 'PA;FI' == cell[:5]:
                        order = int(OR.findall(cell)[0])
                        if na == '让分'and order ==0:
                            full['HASH'].append(float(HA.findall(cell)[0]))
                            full['HASH_ODD'].append(float(odd(OD.findall(cell)[0])))
                            info['HASH_ID'] = 'OV'+ID.findall(cell)[0]+tail
                        elif na == '让分' and order == 1:
                            full['HASA'].append(float(HA.findall(cell)[0]))
                            full['HASA_ODD'].append(float(odd(OD.findall(cell)[0])))
                            info['HASA_ID'] = 'OV'+ID.findall(cell)[0]+tail
                        elif na == '总分' and order == 0:
                            full['HATU'].append(float(HA.findall(cell)[0]))
                            full['HATU_ODD'].append(float(odd(OD.findall(cell)[0])))
                            info['HATU_ID'] = 'OV'+ID.findall(cell)[0]+tail
                        elif na == '总分' and order == 1:
                            full['HATD'].append(float(HA.findall(cell)[0]))
                            full['HATD_ODD'].append(float(odd(OD.findall(cell)[0])))
                            info['HATD_ID'] = 'OV'+ID.findall(cell)[0]+tail
                        elif na == '强弱盘赔率' and order == 0:
                            full['WH_ODD'].append(float(odd(OD.findall(cell)[0])))
                            info['WH_ID'] = 'OV'+ID.findall(cell)[0]+tail
                        elif na == '强弱盘赔率' and order == 1:
                            full['WA_ODD'].append(float(odd(OD.findall(cell)[0])))
                            info['WA_ID'] = 'OV'+ID.findall(cell)[0]+tail
                            dataFull = pd.DataFrame(full)
                            idsFull = [info[key] for key in idKeys]
                            FlagGame = False
                            rowFull = pd.DataFrame(full)
                    break
                # while FlagQuarter:
                #     if 'MA;CN=1' == cell[:7]:
                #         quarter['quarter'].append(na)
                #     elif 'PA;FI' == cell[:5]:
                #         order = int(OR.findall(cell)[0])
                #         if na == '让分'and order ==0:
                #             quarter['HASH'].append(float(HA.findall(cell)[0]))
                #             quarter['HASH_ODD'].append(float(odd(OD.findall(cell)[0])))
                #             info['HASH_ID'] = ID.findall(cell)[0]
                #         elif na == '让分' and order == 1:
                #             quarter['HASA'].append(float(HA.findall(cell)[0]))
                #             quarter['HASA_ODD'].append(float(odd(OD.findall(cell)[0])))
                #             info['HASA_ID'] = ID.findall(cell)[0]
                #         elif na == '强弱盘赔率' and order == 0:
                #             quarter['WH_ODD'].append(float(odd(OD.findall(cell)[0])))
                #             info['Wh_ID'] = ID.findall(cell)[0]
                #         elif na == '强弱盘赔率' and order == 1:
                #             quarter['WA_ODD'].append(float(odd(OD.findall(cell)[0])))
                #             info['WA_ID'] = ID.findall(cell)[0]
                #             dataQuarter = pd.DataFrame(quarter)
                #             rowQuarter = dataQuarter
                #             FlagQuarter =False
                #     break
                # while FlagHalf:
                #     if 'MA;CN=1' == cell[:7]:
                #         na = NA.findall(cell)[0]
                #     elif 'PA;FI' == cell[:5]:
                #         order = int(OR.findall(cell)[0])
                #         if na == '让分'and order ==0:
                #             half['HASH'].append(float(HA.findall(cell)[0]))
                #             half['HASH_ODD'].append(float(odd(OD.findall(cell)[0])))
                #             info['HASH_ID'] = ID.findall(cell)[0]
                #         elif na == '让分' and order == 1:
                #             half['HASA'].append(float(HA.findall(cell)[0]))
                #             half['HASA_ODD'].append(float(odd(OD.findall(cell)[0])))
                #             info['HASA_ID'] = ID.findall(cell)[0]
                #         elif na == '总分' and order == 0:
                #             half['HATU'].append(float(HA.findall(cell)[0]))
                #             half['HATU_ODD'].append(float(odd(OD.findall(cell)[0])))
                #             info['HATU_ID'] = ID.findall(cell)[0]
                #         elif na == '总分' and order == 1:
                #             half['HATD'].append(float(HA.findall(cell)[0]))
                #             half['HATD_ODD'].append(float(odd(OD.findall(cell)[0])))
                #             info['HATD_ID'] = ID.findall(cell)[0]
                #         elif na == '强弱盘赔率' and order == 0:
                #             half['WH_ODD'].append(float(odd(OD.findall(cell)[0])))
                #             info['Wh_ID'] = ID.findall(cell)[0]
                #         elif na == '强弱盘赔率' and order == 1:
                #             half['WA_ODD'].append(float(odd(OD.findall(cell)[0])))
                #             info['WA_ID'] = ID.findall(cell)[0]
                #             dataHalf = pd.DataFrame(half)
                #             rowHalf = dataHalf
                #             ids = [info[key] for key in info.keys() if 'ID' == key[-2:]]
                #             FlagHalf = False
                #     break

                # while FlagInterval:
                #     if 'MA;CN=1' == cell[:7]:
                #         na = NA.findall(cell)[0]
                #     elif 'PA;FI' == cell[:5]:
                #         order = int(OR.findall(cell)[0]))
                #         if na == '让分'and order ==0:
                #             interval['HASH'].append(float(HA.findall(cell)[0]))
                #             interval['HASH_ODD'].append(float(odd(OD.findall(cell)[0])))
                #             info['HASH_ID'] = ID.findall(cell)[0]
                #         elif na == '总分' and order == 1:
                #             interval['HASA'].append(float(HA.findall(cell)[0]))
                #             interval['HASA_ODD'].append(float(odd(OD.findall(cell)[0])))
                #             info['HASA_ID'] = ID.findall(cell)[0]
                #     break

        break
    while Flag3:
        if '\x15' == message[0]:
            for cell in message.split('\x08'):
                try:
                    id = x15x01.findall(cell)[0]
                except:
                    break
                if id in idsFull:
                    for c in BAR.findall(cell)[0][:-1].split(';'):
                        try:
                            element = c.split('=')
                            col = keys(element[0], id, info)
                            check.append(col)
                            if len(check) == len(set(check)):
                                if element[0] =='OD':
                                   rowFull[col] = odd(element[1])
                                   if odd(element[1])==0:
                                       print('\'',element[1],'\':',int(element[1].split('/')[0])/int(element[1].split('/')[1]))
                                elif element[0] =='SS':
                                    rowFull['SC_h'].append(int(element[1][0]))
                                    rowFull['SC_a'].append(int(element[1][1]))
                                else:
                                    try:
                                        rowFull[col] = float(element[1])
                                    except:
                                        rowFull[col] = element[1]
                            elif len(check) != len(set(check)):
                                check = []
                                dataFull = dataFull.append(rowFull)
                                dataFull = dataFull.reset_index(drop=True)
                                check.append(col)
                                if element[0] =='OD':
                                   rowFull[col] = odd(element[1])
                                   if odd(element[1])==0:
                                       print(element[1])
                                elif element[0] =='SS':
                                    rowFull['SC_h'].append(int(element[1][0]))
                                    rowFull['SC_a'].append(int(element[1][1]))
                                else:
                                    try:
                                        rowFull[col] = float(element[1])
                                    except:
                                        rowFull[col] = element[1]
                        except:
                            continue
        break

vc=[]
for m in messages:
    try:
        vc.append(VC.findall(m)[0])
    except:
        continue

    print('\n',repr(m))

p=[x for x in set(dataFull['VC'])]
p.sort()
count = dataFull['VC'].value_counts()

count.shape
set(vc)

d = dataFull[dataFull['VC']==np.nan]
# chrome.ws.settimeout(chrome.timeout)
dataFull[dataFull.duplicated()].shape

24*60/20
