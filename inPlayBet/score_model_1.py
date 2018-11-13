import pandas as pd
import datetime
import os
import numpy as np

def ed(x):
    try:
        q = int(x[1])
    except:
        q = 1
    return q


def score_pred(game):
    game['score'] = game.SC_a + game.SC_h
    game = game[game.VC.notna()]
    game.ED = game.ED.apply(lambda x: ed(x))
    game.TM = (4 - game.ED) * game.TM.values[0] + game.TM
    game['time_q'] = game.apply(lambda row: datetime.timedelta(minutes=row['TM'], seconds=row['TS']).total_seconds(),
                                axis=1)
    game['time_go'] = 2400 - game['time_q']
    game['score_avg'] = game.score / game.time_go
    game['score_pred'] = game['score_avg'] * game['time_q'] + game['score']
    game['dif'] = game.score_pred - game.HATU
    window = game[['time_q', 'TM', 'TS', 'HATU', 'score_pred', 'score', 'score_avg', 'SC_h', 'SC_a','dif']]

    return window
games=[]

for info in os.listdir('D:/code/diffusion/gamepickle'):
    domain = os.path.abspath(r'D:/code/diffusion/gamepickle') #获取文件夹的路径
    info = os.path.join(domain,info) #将路径与文件名结合起来就是每个文件的完整路径
    try:
        game = pd.read_csv(info,engine = 'python')
        window = score_pred(game)
    except:
        continue
    games.append(window)

pass
