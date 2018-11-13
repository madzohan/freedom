import pandas as pd
import datetime
import numpy as np
def vc(x):
    if x in [1082,1083,1084,1087,1088,1089,1090]:
        return 0
    elif x== 11086 :
        return 2
    elif x== 21086 :
        return 1
    else:
        return int(str(x )[0])

def ed(x):
    try:
        q = int(x[0])
    except:
        q = 1
    return q

game = pd.read_csv('../gamepickle/20180917Melaka U21vsNegeri Sembilan U21.csv',engine = 'python')
game =game[game.VC.notna()]
game.ED = game.ED.apply(lambda x: ed(x))
game.TM = (4 - game.ED)* game.TM.values[0] + game.TM
game['VC_1'] = game.VC.apply(lambda x: float(x.split('^')[-1]))
game['time_q'] = game.apply(lambda row:datetime.timedelta(minutes = row['TM'], seconds = row['TS']),axis =1)
# 10:59,
game['time_delta1'] = game['time_q'].shift() - game['time_q']
game['time_delta2'] = game['time_q'].shift(2) - game['time_q']
game['a'] = (game['time_delta1'] > datetime.timedelta( seconds = 56))
game['b'] = (game['time_delta2'] > game['time_delta1'])
game['c'] = game.apply(lambda row: row.b and row.a,axis =1)
game['d'] = (game['time_delta1'] < datetime.timedelta( seconds = 0))
game['e'] = (game['time_delta2'] < datetime.timedelta( seconds = 0))
game['f'] = game.apply(lambda row: row.e and row.d,axis =1)
game = game.drop(game[(game.c ==True)].index)
game = game.drop(game[(game.f ==True)].index)

game['TS_shift'] = (game.TS.shift() -game.TS).apply(lambda x: 1 if x < -40 else 0)
game['count']=game.groupby('TM')['TS_shift'].transform(lambda x: len([y for y in x if y ==1] ))
game['time_delta'] = game['time_q'].shift() - game['time_q']
game =game.drop(['a','b','c','d','e','f'],axis =1)


for by,g in game[game['count'] ==2].groupby("TM"):
    index1 = g.index[(g['count'] == 2) & (g['TS_shift'] == 1)].values[1]
    index2 = g[g['count'] == 2].iloc[-1:].index.values[0]
    game.TM.loc[index1:index2] = g[g['count'] == 2].TM.values[0]-1


game['possession'] =game['VC_1'].apply(lambda x: vc(x))
game['label'] = (game['possession'].shift() - game['possession']).apply(lambda x: 1 if x != 0 else x)
game.loc[game[game['possession']==0].index,'label'] = 0
game['possession_total'] = game.label.rolling(2000,min_periods =1).sum()
game['events'] =game.VC.apply(lambda x: x if x not in [21077,11077] else np.nan)
game['secconds'] =40*60 - game['TM']*60-game['TS']
game['secconds'] = game['secconds'] -game['secconds'].iloc[0]
game['secconds_left'] = 2400 - game['secconds']
game['pace'] =game['secconds']/game['possession_total']
game['score_pace'] = (game['SC_a']+game['SC_h'])/game['possession_total']
game['pred'] = game['secconds_left']*game['score_pace']/game['pace']
game['p'] = 1
quarter = game[game['ED']==1]
g=quarter.groupby('time_q')['p'].mean()
g.sum()

part = game[['possession_total','label',"VC",'TM','TS','SC_a','SC_h']]


possession = game[['VC','possession','label','possession_total','TM','TS','time_delta']]
pass