from nba_playbyplay1 import nba
import pickle
import time
import sys
import os
import pandas as pd
import pymysql
from sqlalchemy import create_engine
id = '73052211C18A_10_0'
sys.argv = [id]
print(sys.argv)
game = nba()
game.parse(sys.argv[-1])
Date = str(time.localtime()[0]) +str(time.localtime()[1])+str(time.localtime()[2])

os.mkdir('gamepickle/'+Date+'/')
gameid = Date+game.info['TeamAway']+'vs'+game.info['TeamHome']
game.dataFull['bet365Id'] = int(sys.argv[-1])
gameinfo = pd.DataFrame({'teamAway':[game.info['TeamAway']],'teamHome':[game.info['TeamHome']],'league':[game.info['League']],'date':[Date]})
with open('gamepickle/'+Date+'/'+'/'+gameid+'.pickle','wb') as f:
    pickle.dump(game.dataFull,f)

cnx = create_engine('mysql+pymysql://root:123456@127.0.0.1:3306/playbyplay?charset=utf8', echo=False)

game.dataFull.to_sql(name='playbyplayBet365', con=cnx, if_exists='append', index=False)
gameinfo.to_sql(name='gameinfo', con=cnx, if_exists='append', index=False)