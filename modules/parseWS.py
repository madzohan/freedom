import time
import re
import json
import pandas as pd
from sqlalchemy import create_engine
import os
import datetime
from twisted.internet import reactor
import pickle

####数据有漏抓的情况，S1,S3
class basketball():

    _INPLAY_SPORTS_SPLIT = re.compile(r'NA=.{2,20};OF=111;')
    _INPLAY_LEAGUES_SPLIT = re.compile(r'CT;FF=;ID=18.*?(?=CT;FF=;ID)')
    _INPLAY_GAMES_SPLIT = re.compile(r'|EV;AU=0;')
    _INPLAY_BASKETBALL_MS = re.compile(r'\|EV;AU=0;C1=1;C2=\d{6,8}.*?(?=\|EV;AU=0;)')
    _INPLAY_SPORTS_OR = re.compile(r'NA=.{2,20};OF=111;OR=\d{0,2}')

    _DELIMITERS_RECORD = '\x01'
    _DELIMITERS_FIELD = '\x02'
    _DELIMITERS_HANDSHAKE = '\x03'
    _DELIMITERS_MESSAGE = '\x08'

    _ENCODINGS_NONE = '\x00'

    _TYPES_TOPIC_LOAD_MESSAGE = '\x14'
    _TYPES_DELTA_MESSAGE = '\x15'
    _TYPES_SUBSCRIBE = '\x16'
    _TYPES_PING_CLIENT = '\x19'
    _TYPES_TOPIC_STATUS_NOTIFICATION = '\x23'

    def __init__(self):
        self.game_ID = re.compile(r'(?<=\x16\x00)\d[\d\w]{5,20}A_10_0(?=\x01$)')
        self.game_IT = re.compile(r'(?<=\x16\x00)\d[\d\w]{5,20}\d_10_0(?=\x01$)')
        self.Handicap = re.compile(r'NA=Handicap 2-Way;.*?(?=MA;CN=1;)')
        self.Total = re.compile(r'NA=Total 2-Way;.*?(?=MA;CN=1;)')
        self.Win = re.compile(r'NA=To Win Match;.*?(?=MA;CN=1;)')
        self.OV_bb = re.compile(r'CT;FF=;ID=18.*?(?=CT;FF=;ID)')
        self.OV_drop = re.compile(r'CT;FF=;ID=18.*?(?=CL;CD=)')
        self.NA = re.compile(r'(?<=NA=).*?(?=;)')  # name
        self.CC = re.compile(r'(?<=CC=).*?(?=;)')
        self.C2 = re.compile(r'(?<=C2=).*?(?=;)')  #
        self.CL = re.compile(r'(?<=CL=).*?(?=;)')
        self.CT = re.compile(r'(?<=CT=).*?(?=;)')  # league
        self.CP = re.compile(r'(?<=CP=)\w*?(?=;)')  #
        self.ED = re.compile(r'(?<=ED=).*?(?=;)')  # quarter
        self.ID = re.compile(r'(?<=ID=)\w*?(?=;)')
        self.IT = re.compile(r'(?<=IT=)\w*?(?=;)')
        self.S1 = re.compile(r'(?<=S1=).*?(?=;)')
        self.S2 = re.compile(r'(?<=S2=).*?(?=;)')
        self.S3 = re.compile(r'(?<=S3=).*?(?=;)')
        self.S4 = re.compile(r'(?<=S4=).*?(?=;)')
        self.S5 = re.compile(r'(?<=S5=).*?(?=;)')
        self.S6 = re.compile(r'(?<=S6=).*?(?=;)')
        self.S7 = re.compile(r'(?<=S7=).*?(?=;)')
        self.S8 = re.compile(r'(?<=S8=).*?(?=;)')
        self.SC = re.compile(r'(?<=SC=).*?(?=;)')
        self.SS = re.compile(r'(?<=SS=).*?(?=;)')
        self.SU = re.compile(r'(?<=SU=).*?(?=;)')
        self.TM = re.compile(r'(?<=TM=).*?(?=;)')  # minute
        self.TS = re.compile(r'(?<=TS=).*?(?=;)')  # second
        self.TU = re.compile(r'(?<=TU=).*?(?=;)')  # time update
        self.TT = re.compile(r'(?<=TT=).*?(?=;)')  # time TICKING
        self.TD = re.compile(r'(?<=TD=).*?(?=;)')  # COUNTDOWN, TAX_DETAILS
        self.HA = re.compile(r'(?<=HA=).*?(?=;)')  # handicap
        self.OD = re.compile(r'(?<=OD=).*?(?=;)')  # odds
        self.OR = re.compile(r'(?<=OR=)\d{0,2}(?=;)')
        self.FI = re.compile(r'(?<=HA=).*?(?=;)')
        self.EV = re.compile(r'EV;AU.+?OR=1;PX=;SU=\d;')
        self.VC = re.compile(r'(?<=VC=).*?(?=;)')
        self.x15x01 = re.compile(r'(?<=\x15).*?(?=\x01)')
        self.x16x01 = re.compile(r'(?<=\x16).*?(?=\x01)')
        self.x14x01 = re.compile(r'(?<=\x14).*?(?=\x01)')
        self.x15x08 = re.compile(r'(?<=\x15).*?(?=\x08)')
        self.x08x01 = re.compile(r'(?<=\x08).*?(?=\x01)')
        self.BAR = re.compile(r'(?<=\|).*?(?=\|)')
        self.full ={}
        self.tail = '_1_3'
        self.info = {}
        self.check = []
        self.line = {}
        self.ids = []
        self.idsFull =[]
        self.idKeys = ['GameIT','GameID',  'TeamHomeIT', 'TeamAwayIT', 'HASH_ID', 'HASA_ID', 'HATU_IT', 'HATD_IT', 'WH_IT', 'WA_IT']
        self.full = {}
        self.GameOver = False
        self.messages =[]
        self.Flag = False
        self.Flag1 = False
        self.Flag2 = False
        self.f1 = False
        self.f2 = False
        self.f = False

    def parse_OVInPlay(self,message):
        games = []
        basketball = self._INPLAY_BASKETBALL_MS.findall(message)
        for cell in basketball:
            dict ={}
            dict['messages'] = '15'+self.C2.findall(cell)[0]+'5M18_1_3'+'@'+self.ID.findall(cell)[0]+'@'+self.NA.findall(cell)[0]
            dict['games'] = self.NA.findall(cell)[0]
            games.append(dict)
        return games

    def parseIT(self,message,id,it):
        self.info['GameID'] = id
        self.info['GameIT'] = it
        try:
            handicap = self.Handicap.findall(message)[0]
            handicaps = self.BAR.findall(handicap)
            self.full['ED'] = [float(self.ED.findall(message)[0][0])]
            self.full['HASH'] = [float(self.HA.findall(handicaps[1])[0])]
            self.full['HASH_ODD'] = [float(self.odds(self.OD.findall(handicaps[1])[0]))]
            self.info['HASH_ID'] = 'OV' + self.ID.findall(handicaps[1])[0] + self.tail
            self.full['HASA'] = [float(self.HA.findall(handicaps[2])[0])]
            self.full['HASA_ODD'] = [float(self.odds(self.OD.findall(handicaps[2])[0]))]
            self.info['HASA_ID'] = 'OV' + self.ID.findall(handicaps[2])[0] + self.tail

            total = self.Total.findall(message)[0]
            totals = self.BAR.findall(total)
            self.full['HATU'] = [float(self.HA.findall(totals[1])[0])]
            self.full['HATU_ODD'] = [float(self.odds(self.OD.findall(totals[1])[0]))]
            self.info['HATU_IT'] = self.IT.findall(totals[1])[0]
            self.full['HATD'] = [float(self.HA.findall(totals[2])[0])]
            self.full['HATD_ODD'] = [float(self.odds(self.OD.findall(totals[2])[0]))]
            self.info['HATD_IT'] = self.IT.findall(totals[2])[0]

            win = self.Win.findall(message)[0]
            wins = self.BAR.findall(win)
            self.full['WH_ODD'] = [float(self.odds(self.OD.findall(wins[1])[0]))]
            self.info['WH_IT'] = self.IT.findall(wins[1])[0]
            self.full['WA_ODD'] = [float(self.odds(self.OD.findall(wins[2])[0]))]
            self.info['WA_IT'] = self.IT.findall(wins[2])[0]
        except:
            pass
        keys =  [ y for y in self.idKeys if y in [x for x in self.info]]
        self.idsFull = [self.info[key] for key in keys ]+['6V'+id,'6V'+it]
        self.dataFull = pd.DataFrame(self.full)
        self.rowFull = pd.DataFrame(self.full)
        print('更新IT！！！！！', self.idsFull)

    def parseVC(self,topic,message,flag):
        # try:
        #     print(self.info['TeamAway'], self.info['TeamHome'],flag)
        # except:
        #     pass
        if topic in self.idsFull:
            for c in self.BAR.findall(message)[0].split(';')[:-1]:
                element = c.split('=')
                if element[0] in ['HD','LA','SU']:
                    continue
                if element[0] in ['XY']:
                    continue
                col = self.keys(element[0], topic)
                self.check.append(col)
                if len(self.check) == len(set(self.check)):
                    if element[0] =='OD':
                       self.rowFull[col] = self.odds(element[1])
                    elif element[0] =='SS':
                            self.rowFull['SC_h'] = int(element[1].split('-')[1])
                            self.rowFull['SC_a'] = int(element[1].split('-')[0])
                    else:
                        try:
                            self.rowFull[col] = float(element[1])
                        except:
                            try:
                                self.rowFull[col] = element[1]
                            except:
                                pass
                try:
                    if self.rowFull['VC'].values[0] == 1084:
                        print("first")
                        if self.dataFull['SC_h'].values[-1] != self.dataFull['SC_a'].values[-1]:
                            print('比赛结束哦', self.info['TeamAway'], self.info['TeamHome'])
                            self.GameOver = True
                            self.dataFull = self.dataFull.append(self.rowFull)
                            self.dataFull = self.dataFull.reset_index(drop=True)
                            self.save()
                            try:
                                reactor.callFromThread(reactor.stop)
                            except:
                                pass
                except:
                    pass
        if len(self.check) != len(set(self.check)) and flag ==0:
            p = self.rowFull
            try:
                ed= int(p.ED.iloc[0][0])
            except:
                try:
                    ed =p.ED.iloc[0]
                except:
                    pass

            try:
                time_q = 12
                total = (p.SC_a+p.SC_h)[0]
                tm = (4 - ed)* time_q + self.rowFull['TM'][0]
                t = datetime.timedelta(minutes=tm, seconds=self.rowFull['TS'][0]).total_seconds()
                t_pass = time_q*4*60 - t
                avg = total/t_pass
                pred = time_q*4*60*avg
                dif = pred - self.rowFull['HATU'][0]
                pace_line = (self.rowFull['HATU'][0] - total)*60/t
                pace_pred = avg*60
                print(self.info['TeamAway'], self.info['TeamHome'],self.rowFull['ED'][0],self.rowFull['TM'][0],self.rowFull['TS'][0],pace_line,pace_pred,'[ %f ]' %(pace_line-pace_pred),round(pace_line*time_q))
                print('pred:',pred,'line:',self.rowFull['HATU'][0],self.rowFull['SC_h'][0],self.rowFull['SC_a'][0]
                      , '[ %d ]' %dif, '[ %d ]' %dif, '[ %d ]' %dif, '[ %d ]' %dif, '[ %d ]' %dif)
            except:
                pass
            self.check = []
            self.dataFull = self.dataFull.append(self.rowFull)
            self.dataFull = self.dataFull.reset_index(drop=True)



    def odds(self,x):
        x = x.split('/')
        try:
            odds = int(x[0]) / int(x[1])
        except:
            odds = 0
        return odds
    def keys(self,x,id):
        try:
            if id == self.info['HASH_ID']:
                return {'HA': 'HASH','HD': 'HASH','OD': 'HASH_ODD'}.get(x, x)
            elif id == self.info['HASA_ID']:
                return {'HA': 'HASA','HD': 'HASA','OD': 'HASA_ODD'}.get(x, x)
            elif id == self.info['HATU_IT']:
                return {'HA': 'HATU','HD': 'HATU','LA': 'HATU','OD': 'HATU_ODD'}.get(x, x)
            elif id == self.info['HATD_IT']:
                return {'HA': 'HATD','HD': 'HATD','LA': 'HATD','OD': 'HATD_ODD'}.get(x, x)
            if id == self.info['TeamHomeIT']:
                return {'S1': 'S1_h', 'S2': 'S2_h', 'S3': 'S3_h', 'S4': 'S4_h', 'S5': 'S5_h', 'S6': 'S6_h', 'SC': 'SC_h'}.get(x, x)
            elif id == self.info['TeamAwayIT']:
                return {'S1': 'S1_a','S2': 'S2_a','S3': 'S3_a','S4': 'S4_a','S5': 'S5_a','S6': 'S6_a','SC': 'SC_a'}.get(x, x)
            elif id == self.info['WH_IT']:
                return {'OD': 'WH_ODD'}.get(x, x)
            elif id == self.info['WA_IT']:
                return {'OD': 'WA_ODD'}.get(x, x)
            else:
                return x
        except:
            return x
    def parseID(self,message): # cells[0]:EV;C1=1;C2=5201380;CK=20448857;CL=18;CT=NBA;DC=1;ED=第3节;EL=0;EX=;ID=70869704C18A_10_0;IT=1552013805M18_10_0;LB=;MD=2;ML=0;NA=洛杉矶湖人 @ 奥兰多魔术;PG=2;S1=3分球;S2=2分球;S3=罚球;S4=暂停;S5=犯规;S6=;S7=;SB=0;SS=51-58;SV=1;T1=5;T2=5;TA=;TD=1;TM=12;TS=0;TT=0;TU=;VC=1082;XT=0;XY=;
        cells = self.BAR.findall(message.split('\x01')[-1])
        self.info['League'] = self.CT.findall(cells[0])[0]
        self.full['ED'] = [self.ED.findall(cells[0])[0]]
        na = self.NA.findall(cells[0])[0]
        self.info['TeamAway'] = re.split(r'\s(@|v|vs)\s', na)[0].strip()
        self.info['TeamHome'] = re.split(r'\s(@|v|vs)\s', na)[-1].strip()
        # print(na)
        # self.full['SC_a'] = [int( SS.findall(cells[0])[0].split('-')[1]))
        # self.full['SC_h'] = [int(SS.findall(cells[0])[0].split('-')[0]))
        self.full['TM'] = [int(self.TM.findall(cells[0])[0])]
        self.full['TS'] = [int(self.TS.findall(cells[0])[0])]
        self.full['TU'] = [self.TU.findall(cells[0])[0]]
        self.full['TT'] = [self.TT.findall(cells[0])[0]]
        self.full['TD'] = [self.TD.findall(cells[0])[0]]
        self.full['SU'] = [0]
        try:
            self.full['VC'] = [self.VC.findall(cells[0])[0]]
        except:
            self.full['VC'] = ['0']
        for cell in cells[0:10]:
            try:
                if self.info['TeamAway'] == self.NA.findall(cell)[0]:
                    self.info['TeamAwayIT'] = self.IT.findall(cell)[0]
                    self.full['S1_a'] = [int(self.S1.findall(cell)[0])]
                    self.full['S2_a'] = [int(self.S2.findall(cell)[0])]
                    self.full['S3_a'] = [int(self.S3.findall(cell)[0])]
                    self.full['S4_a'] = [int(self.S4.findall(cell)[0])]
                    self.full['S5_a'] = [int(self.S5.findall(cell)[0])]
                    self.full['S6_a'] = [float(self.S6.findall(cell)[0])]
                    self.full['SC_a'] = [int(self.SC.findall(cell)[0])]
                elif self.info['TeamHome'] == self.NA.findall(cell)[0]:
                    self.info['TeamHomeIT'] = self.IT.findall(cell)[0]
                    self.full['S1_h'] = [int(self.S1.findall(cell)[0])]
                    self.full['S2_h'] = [int(self.S2.findall(cell)[0])]
                    self.full['S3_h'] = [int(self.S3.findall(cell)[0])]
                    self.full['S4_h'] = [int(self.S4.findall(cell)[0])]
                    self.full['S5_h'] = [int(self.S5.findall(cell)[0])]
                    self.full['S6_h'] = [float(self.S6.findall(cell)[0])]
                    self.full['SC_h'] = [int(self.SC.findall(cell)[0])]
            except:
                continue

    def save(self):
        Date = datetime.datetime.today().strftime('%Y%m%d')
        try:
            os.mkdir('gamepickle/')
        except:
            print('文件已存在')
        gameid = Date + self.info['TeamAway'] + 'vs' + self.info['TeamHome']
        with open('gamepickle/' + gameid + '.csv', 'w') as f:
            self.dataFull.to_csv(f)

if __name__ =='__main__':

    with open('../ovinplay_message.txt', 'r') as f:
        message = f.read()
    bb = basketball()
    bb.parse_OvInPlay(message)