import time
import re
import json
import pandas as pd
from sqlalchemy import create_engine

class nba():

    def __init__(self,chrome):
        self.chrome = chrome
        self.OV_bb = re.compile(r'CT;FF=;ID=18.*?(?=CT;FF=;ID)')
        self.OV_drop = re.compile(r'CT;FF=;ID=18.*?(?=CL;CD=)')
        self.NA = re.compile(r'(?<=NA=).*?(?=;)')  # name
        self.CC = re.compile(r'(?<=CC=).*?(?=;)')  #
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
        self.OR = re.compile(r'(?<=OR=).*?(?=;)')  # order
        self.FI = re.compile(r'(?<=HA=).*?(?=;)')
        self.EV = re.compile(r'EV;AU.+?OR=1;PX=;SU=\d;')
        self.VC = re.compile(r'(?<=VC=).*?(?=;)')
        self.x15x01 = re.compile(r'(?<=\x15).*?(?=\x01)')
        self.x14x01 = re.compile(r'(?<=\x14).*?(?=\x01)')
        self.x15x08 = re.compile(r'(?<=\x15).*?(?=\x08)')
        self.x08x01 = re.compile(r'(?<=\x08).*?(?=\x01)')
        self.BAR = re.compile(r'(?<=\|).*?(?=\|)')

        self.full ={}
        self.tail = '_10_0'
        self.info = {}
        self.check = []
        self.line = {}
        self.ids = []
        self.idsFull =[]
        self.idKeys = ['GameIT', 'TeamHomeIT', 'TeamAwayIT', 'HASH_ID', 'HASA_ID', 'HATU_ID', 'HATD_ID', 'WH_ID', 'WA_ID']
        self.full = {}
        self.GameOver = False
        self.messages =[]


    def odd(self,x):
        return{'1/1':1,'3/4':0.75,'4/5':0.8,'4/6':0.66,'5/4': 1.25,'5/6':0.83,'5/8': 0.63,'5/11':0.45,'5/7':0.71,'5/9': 0.56,'6/4': 1.5,'6/7':0.86,'6/5':1.2,
               '7/4':1.75,'8/9':0.89,'10/11':0.91,'10/13':0.77,'10/21': 0.47,'11/10':1.1,'13/10': 1.3,'17/10': 1.7,'20/21':0.95,
               '20/23':0.87,'20/27':0.74,'20/29':0.69,'20/33': 0.61,'20/31':0.65,'21/20':1.05,'23/20':1.15,'27/20': 1.35}.get(x,0)
    def keys(self,x,id):
        try:
            if id == self.info['TeamHomeIT']:
                return {'S1': 'S1_h','S2': 'S2_h','S3': 'S3_h','S4': 'S4_h','S5': 'S5_h','S6': 'S6_h','SC': 'SC_h'}.get(x, x)
            elif id == self.info['TeamAwayIT']:
                return {'S1': 'S1_a','S2': 'S2_a','S3': 'S3_a','S4': 'S4_a','S5': 'S5_a','S6': 'S6_a','SC': 'SC_a'}.get(x, x)
            elif id == self.info['HASH_ID']:
                return {'HA': 'HASH','OD': 'HASH_ODD'}.get(x, x)
            elif id == self.info['HASA_ID']:
                return {'HA': 'HASA','OD': 'HASA_ODD'}.get(x, x)
            elif id == self.info['HATU_ID']:
                return {'HA': 'HATU','OD': 'HATU_ODD'}.get(x, x)
            elif id == self.info['HATD_ID']:
                return {'HA': 'HATD','OD': 'HATD_ODD'}.get(x, x)
            elif id == self.info['WH_ID']:
                return {'OD': 'WH_ODD'}.get(x, x)
            elif id == self.info['WA_ID']:
                return {'OD': 'WA_ODD'}.get(x, x)
            else:
                return x
        except:
            return x
    def evcl(self,cells): # cells[0]:EV;C1=1;C2=5201380;CK=20448857;CL=18;CT=NBA;DC=1;ED=第3节;EL=0;EX=;ID=70869704C18A_10_0;IT=1552013805M18_10_0;LB=;MD=2;ML=0;NA=洛杉矶湖人 @ 奥兰多魔术;PG=2;S1=3分球;S2=2分球;S3=罚球;S4=暂停;S5=犯规;S6=;S7=;SB=0;SS=51-58;SV=1;T1=5;T2=5;TA=;TD=1;TM=12;TS=0;TT=0;TU=;VC=1082;XT=0;XY=;
        self.info['League'] = self.CT.findall(cells[0])[0]
        self.full['ED'] = [self.ED.findall(cells[0])[0]]
        self.info['GameID'] = self.ID.findall(cells[0])[0]
        self.info['GameIT'] = self.IT.findall(cells[0])[0]
        na = self.NA.findall(cells[0])[0]
        self.info['TeamAway'] = re.split(r'@|v|vs', na)[0].strip()
        self.info['TeamHome'] = re.split(r'@|v|vs', na)[1].strip()
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
            print('error')
        for cell in cells[1:10]:
            try:
                if self.info['TeamAway'] == self.NA.findall(cell)[0]:
                    self.full['S1_a'] = [int(self.S1.findall(cell)[0])]
                    self.full['S2_a'] = [int(self.S2.findall(cell)[0])]
                    self.full['S3_a'] = [int(self.S3.findall(cell)[0])]
                    self.full['S4_a'] = [int(self.S4.findall(cell)[0])]
                    self.full['S5_a'] = [int(self.S5.findall(cell)[0])]
                    self.full['S6_a'] = [float(self.S6.findall(cell)[0])]
                    self.full['SC_a'] = [int(self.SC.findall(cell)[0])]
                    self.info['TeamAwayIT'] = self.IT.findall(cell)[0]
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


    def gameOdds(self, cell,na):
            order = int(self.OR.findall(cell)[0])
            if na == '让分' and order == 0:
                self.full['HASH'] = [float(self.HA.findall(cell)[0])]
                self.full['HASH_ODD'] = [float(self.odd(self.OD.findall(cell)[0]))]
                self.info['HASH_ID'] = 'OV' + self.ID.findall(cell)[0] + self.tail
            elif na == '让分' and order == 1:
                self.full['HASA'] = [float(self.HA.findall(cell)[0])]
                self.full['HASA_ODD'] = [float(self.odd(self.OD.findall(cell)[0]))]
                self.info['HASA_ID'] = 'OV' + self.ID.findall(cell)[0] + self.tail
            elif na == '总分' and order == 0:
                self.full['HATU'] = [float(self.HA.findall(cell)[0])]
                self.full['HATU_ODD'] = [float(self.odd(self.OD.findall(cell)[0]))]
                self.info['HATU_ID'] = 'OV' + self.ID.findall(cell)[0] + self.tail
            elif na == '总分' and order == 1:
                self.full['HATD'] = [float(self.HA.findall(cell)[0])]
                self.full['HATD_ODD'] = [float(self.odd(self.OD.findall(cell)[0]))]
                self.info['HATD_ID'] = 'OV' + self.ID.findall(cell)[0] + self.tail
            elif na == '强弱盘赔率' and order == 0:
                self.full['WH_ODD'] = [float(self.odd(self.OD.findall(cell)[0]))]
                self.info['WH_ID'] = 'OV' + self.ID.findall(cell)[0] + self.tail
            elif na == '强弱盘赔率' and order == 1:
                self.full['WA_ODD'] = [float(self.odd(self.OD.findall(cell)[0]))]
                self.info['WA_ID'] = 'OV' + self.ID.findall(cell)[0] + self.tail

    def parse(self,id):
        self.chrome.Page.reload()###要不后面采不到'EV;C1=' in message
        f1 = True
        f2 = True
        FlagGame = False
        FlagQuarter = False
        FlagHalf = False
        FlagInterval = False
        Flag1 = f1 or f2
        Flag2 = not Flag1
        Flag_ADD = False
        messages =[]
        while True:
            try:
                message = self.chrome.ws.recv()
                if 'webSocketFrameReceived' in message[:45]:
                    message = json.loads(message)['params']['response']['payloadData']
                    messages.append(message)
            except:
                continue
            while Flag1:
                if 'EV;C1=' in message:
                    if id == self.ID.findall(message)[0] :
                        f1 = False
                        cells = self.BAR.findall(message.split('\x01')[-1])
                        self.evcl(cells)
                    break

                elif id in message and 'F|EV;' in message:
                    f2 = False
                    cells = self.BAR.findall(message)
                    for cell in cells:
                        if 'MG;4Q' == cell[:5]:
                            na = self.NA.findall(cell)[0]
                            if na =='比赛投注':
                                FlagGame = True
                            elif '节投注' in na:
                                FlagGame = False
                                FlagQuarter = True
                            elif na == '上半场投注':
                                FlagGame = False
                                FlagHalf = True
                            elif na == '输赢比数':
                                FlagGame = False
                                FlagInterval = True

                        while FlagGame:
                            if 'MA;CN=1' == cell[:7]:
                                na = self.NA.findall(cell)[0]
                            elif 'PA;FI' == cell[:5]:
                                self.gameOdds(cell,na)
                            break

                self.dataFull = pd.DataFrame(self.full)
                keys =  [ y for y in self.idKeys if y in [x for x in self.info]]
                self.idsFull = [self.info[key] for key in keys ]
                self.rowFull = pd.DataFrame(self.full)
                Flag1 = f1 or f2
                Flag2 = not Flag1
                        # while FlagQuarter:
                        #     if 'MA;CN=1' == cell[:7]:
                        #         na = self.NA.findall(cell)[0]
                        #     elif 'PA;FI' == cell[:5]:
                        #         self.quarterOdds(cell,na)
                        #         break
                        # while FlagHalf:
                        #     if 'MA;CN=1' == cell[:7]:
                        #         na = self.NA.findall(cell)[0]
                        #     elif 'PA;FI' == cell[:5]:
                        #         self.halfOdds(cell,na)
                        #         break
                        # while FlagInterval:
                        #     if 'MA;CN=1' == cell[:7]:
                        #         na = self.NA.findall(cell)[0]
                        #     elif 'PA;FI' == cell[:5]:
                        #         self.intervalOdds(cell,na)
                        #         break
                break
            while Flag2:
                if '\x15' == message[0]:
                    for cell in message.split('\x08'):
                        try:
                            id = self.x15x01.findall(cell)[0]
                        except:
                            break
                        if id in self.idsFull:
                            print(id)
                            cookies = self.chrome.Network.getCookies()
                            for cookie in cookies['result']['cookies']:
                                print(id,cookie)
                            for c in self.BAR.findall(cell)[0][:-1].split(';'):
                                try:
                                    element = c.split('=')
                                    col = self.keys(element[0], id)
                                    self.check.append(col)
                                    # if element[0] == 'VC':
                                    #     print(element)
                                    if len(self.check) == len(set(self.check)):
                                        if element[0] =='OD':
                                           self.rowFull[col] = self.odd(element[1])
                                           if self.odd(element[1])==0:
                                               print('\'',element[1],'\':',int(element[1].split('/')[0])/int(element[1].split('/')[1]))
                                        elif element[0] =='SS':
                                            self.rowFull['SC_h'].append(int(element[1][0]))
                                            self.rowFull['SC_a'].append(int(element[1][1]))

                                        else:
                                            try:
                                                self.rowFull[col] = float(element[1])
                                            except:
                                                self.rowFull[col] = element[1]
                                            if self.rowFull['VC'].values[0] in [1083]:# if self.rowFull['TM'] == 0 or self.rowFull['TS'] == 0:
                                                # if self.rowFull['ED'] in ['第4节']:
                                                #     if self.rowFull['SC_h'] != self.rowFull['SC_a']:
                                                self.dataFull = self.dataFull.append(self.rowFull)
                                                self.dataFull = self.dataFull.reset_index(drop=True)
                                    elif len(self.check) != len(set(self.check)):
                                        self.check = []
                                        self.dataFull = self.dataFull.append(self.rowFull)
                                        self.dataFull = self.dataFull.reset_index(drop=True)
                                        self.check.append(col)
                                        # print(self.info['GameID'])
                                        if element[0] =='OD':
                                           self.rowFull[col] = self.odd(element[1])
                                           if self.odd(element[1])==0:
                                               print(element[1])
                                        elif element[0] =='SS':
                                            self.rowFull['SC_h'].append(int(element[1][0]))
                                            self.rowFull['SC_a'].append(int(element[1][1]))
                                        else:
                                            try:
                                                self.rowFull[col] = float(element[1])
                                            except:
                                                self.rowFull[col] = element[1]
                                        if self.rowFull['VC'] in [1082,1083,1084]:# if self.rowFull['TM'] == 0 or self.rowFull['TS'] == 0:
                                            if self.rowFull['ED'] in ['第4节']:
                                                if self.rowFull['SC_h'] != self.rowFull['SC_a']:
                                                    self.GameOver = True
                                except:
                                    continue

                break
            if self.GameOver:
                print('game over')
                Date = str(time.localtime()[0]) + str(time.localtime()[1]) + str(time.localtime()[2])
                gameid = Date + self.info['TeamAway'] + 'vs' + self.info['TeamHome']
                # game.dataFull['bet365Id'] = int(id)
                gameinfo = pd.DataFrame(
                    {'teamAway': [self.info['TeamAway']], 'teamHome': [self.info['TeamHome']],
                     'league': [self.info['League']],
                     'date': [Date]})
                with open('gamepickle/' + Date + '/' + '/' + gameid + '.csv', 'w') as f:
                    self.dataFull.to_csv(f)

                cnx = create_engine('mysql+pymysql://root:123456@127.0.0.1:3306/playbyplay?charset=utf8', echo=False)
                self.dataFull.to_sql(name='playbyplayBet365', con=cnx, if_exists='append', index=False)
                gameinfo.to_sql(name='gameinfo', con=cnx, if_exists='append', index=False)
                # self.chrome.Target.closeTarget(target_id = targetID)
                #return self.dataFull
                break







# for message in messages:
#     if 'F|EV;' in message:
#         print(repr(message))

# self.idsFull
# 1551967235M18_10_0