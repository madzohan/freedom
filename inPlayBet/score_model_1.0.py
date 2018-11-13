import pymysql
import pandas as pd
from datetime import timedelta
import numpy as np
from scipy.stats import kurtosis, skew,linregress
import pickle

class inplay():

    def __init__(self):
        self.timedelta_5 = timedelta(minutes =6)
        self.timedelta_10 = timedelta(minutes=11)
        self.timedelta_100 = timedelta(minutes=100)

    def read_sql(self):
        connection = pymysql.connect(host='localhost',
                                     user='root',
                                     port=3306,
                                     password='123456',
                                     db='nowgoal_nba',
                                     charset='utf8',
                                     )
        sql = """ select game_id,line,odds_l,odds_r,quarter,score_a,score_h,time_q 
                  from crown_total_info where status = 'Run'
                  limit 100000,200000"""
        sql1 = """ select game_id,score_home,score_away,league from game_info"""
        data = pd.read_sql(sql, con=connection)
        game_info = pd.read_sql(sql1, con=connection)
        return data, game_info

    def feature(self,g):
        timedelta(minutes=5)
        g.dtypes
        odds_avg = (g['odds_l'] + g['odds_r']).mean() / 2
        g['pace'] =g['score']/g['time'].apply(lambda x: x.seconds)*60
        g['pace_line'] = (g['line'] -g['score'])/g['time_t'].apply(lambda x: x.seconds)*60
        g['pace_dif'] = g['pace_line'] - g['pace']
        g['score_dif'] = g['score'].diff(1)
        g= g.set_index('index_time')
        time_5 = g[g['time']<=self.timedelta_5].shape[0]
        time_10 = g[g['time'] <= self.timedelta_10].shape[0]
        g['pace_last_5'] = g['score_dif'].rolling(self.timedelta_5,min_periods = time_5).sum()/5
        g['pace_last_10'] = g['score_dif'].rolling(self.timedelta_10,min_periods = time_10).sum() / 10
        g['pace_max_5'] = g['pace_last_5'].rolling(self.timedelta_5,min_periods = 1).max()
        g['pace_min_5'] = g['pace_last_5'].rolling(self.timedelta_5, min_periods=1).apply(np.nanmin)
        g['pace_max_10'] = g['pace_last_10'].rolling(self.timedelta_5, min_periods=1).max()
        g['pace_min_10'] = g['pace_last_10'].rolling(self.timedelta_5, min_periods=1).apply(np.nanmin)
        g['line_skew'] = g['line'].rolling(self.timedelta_5, min_periods=1).apply(skew)
        g['line_kurtosis'] = g['line'].rolling(self.timedelta_5, min_periods=1).apply(kurtosis)
        g['line_slope'] = g['line'].rolling(self.timedelta_5, min_periods=5).apply(lambda x:self.line_slope(x))
        for index,row in g.iterrows():
            begin = max(timedelta(seconds=0),index - self.timedelta_5)
            if index >self.timedelta_5:
                g.loc[index,'line_lowOdds'] = self.odds_dist(g.loc[begin:index,:],'lowOdds',odds_avg)
                g.loc[index, 'line_highOdds'] = self.odds_dist(g.loc[begin:index, :], 'highOdds', odds_avg)
                g.loc[index, 'count_lowOdds'] = self.odds_dist(g.loc[begin:index, :], 'lowCount', odds_avg)
                g.loc[index, 'count_highOdds'] = self.odds_dist(g.loc[begin:index, :], 'highCount', odds_avg)
        return g

    def line_slope(self,x):
        slope, intercept, r_value, p_value, std_err = linregress(range(len(x)), x)
        return slope
    def odds_dist(self,g,type,odds_avg):
        if type == 'lowOdds':
            return g[g['odds_r']+0.005 < odds_avg]['line'].mean()
        elif type ==  'highOdds':
            return g[g['odds_r']-0.005 > odds_avg]['line'].mean()
        elif type == 'lowCount':
            return g[g['odds_r']+0.005< odds_avg]['line'].shape[0]
        elif type == 'highCount':
            return g[g['odds_r']-0.005 > odds_avg]['line'].shape[0]

    def quarter_time(self,x):
        try:
            t = timedelta(minutes=int(x.split(':')[0]), seconds=int(x.split(':')[1]))
        except:
            t = 0
        return t
    def process(self):
        data,game_info =self.read_sql()
        try:
            game_info['score_final'] = game_info['score_home']+game_info['score_away']
            data = data[data['line'] !='0']
            data = data[data['quarter'] !='0']
            data['time_q'] = data['time_q'].apply(lambda x: self.quarter_time(x))
            data = data[data['time_q'] != 0]

            data['score'] = data['score_h'] +data['score_a']
            data['line'] = data['line'].apply(lambda x: float(x))
            data_run = data
            # data_run = data_run.drop(['status'],axis =1)
            data_run = data_run.merge(game_info[['game_id','score_final']],how ='left',on = 'game_id')
            data_run['cover'] =  data_run['line'] - data_run['score_final']
            data_run['pick'] = data_run['cover'].apply(lambda x: self.pick(x))
            data_final = pd.DataFrame()
        except:
            pass
        for index,group in data_run.groupby('game_id'):
            if  group['time_q'].max() < timedelta(minutes=11):
                group['time_t'] = (4 - group['quarter'].apply(lambda x: int(x))) * (group['time_q'].max()) + group['time_q']
                group['time_ts'] = group['time_t'].apply(lambda x:x.seconds)
                group['time_qs'] = group['time_q'].apply(lambda x: x.seconds)
                group['time'] = 4 * (group['time_q'].max()) - group['time_t']
                group['game_time'] = 4 * (group['time_q'].max())
                group = group.sort_values(['time','score'])
                group['index_time'] = group['time']
                g = self.feature(group)
                data_final = data_final.append(g)
        return data_final

    def pick(self,x):
        if x >0:
            return 1
        # elif x<=-5:
        #     return 1
        else:
            return 0

    def save_to_pickle(self,data):
        with open('nba.pickle','wb') as f:
            pickle.dump(data,f)
if __name__ == '__main__':
    p = inplay()
    data = p.process()
    p.save_to_pickle(data)
    ['line','odds_l','odds_r','score_a','score_h','pick','time_ts','time_qs','pace','pace_line', 'pace_dif',
     'score_dif', 'pace_last_5', 'pace_last_10', 'pace_max_5', 'pace_min_5', 'pace_max_10', 'pace_min_10',
     'line_skew', 'line_kurtosis', 'line_slope', 'line_lowOdds', 'line_highOdds', 'count_lowOdds', 'count_highOdds']