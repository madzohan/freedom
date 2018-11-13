import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn import cross_validation, metrics
import sys
import matplotlib.pylab as plt
from xgboost.sklearn import XGBClassifier
from sklearn.model_selection import GridSearchCV
import codecs
import pickle
from sklearn.model_selection import train_test_split


def modelfit(alg, dtrain, dtest, predictors, target, metric, useTrainCV=True, cv_folds=5, early_stopping_rounds=50):
    if useTrainCV:
        xgb_param = alg.get_xgb_params()
        xgtrain = xgb.DMatrix(dtrain[predictors].values, label=dtrain[target].values)
        xgtest = xgb.DMatrix(dtest[predictors].values)
        cvresult = xgb.cv(xgb_param, xgtrain, num_boost_round=alg.get_params()['n_estimators'], nfold=cv_folds,
                          metrics=metric, early_stopping_rounds=early_stopping_rounds)
        print(cvresult.shape[0])
        alg.set_params(n_estimators=cvresult.shape[0])

    # Fit the algorithm on the data
    alg.fit(dtrain[predictors], dtrain[target], eval_metric=metric)

    # Predict training set:
    dtrain_predictions = alg.predict(dtrain[predictors])
    dtrain_predprob = alg.predict_proba(dtrain[predictors])[:, 1]

    # Print model report:
    print("\nModel Report")
    print("Accuracy : %.4g" % metrics.accuracy_score(dtrain[target].values, dtrain_predictions))
    print("AUC Score (Train): %f" % metrics.roc_auc_score(dtrain[target], dtrain_predprob))


    feat_imp = pd.Series(alg.feature_importances_, index=alg._Booster.feature_names).sort_values(ascending=False)
    feat_imp.plot(kind='bar', title='Feature Importances')
    plt.ylabel('Feature Importance Score')
    plt.show()
    return feat_imp



with open('nba_2.pickle','rb') as f:
    data = pickle.load(f)

data =data.reset_index()
train= data.iloc[:int(round(data.shape[0]*0.7)),:]
test = data.drop(train.index)
train.shape,test.shape

target='pick'
predictors = ['line','odds_l','odds_r','score_a','score_h','time_ts','time_qs','pace','pace_line', 'pace_dif',
      'pace_last_5', 'pace_last_10', 'pace_max_5', 'pace_min_5', 'pace_max_10', 'pace_min_10',
     'line_skew', 'line_kurtosis', 'line_slope', 'line_lowOdds', 'line_highOdds', 'count_lowOdds', 'count_highOdds']
predictors = ['line','score_a','score_h','time_ts','pace','pace_line',
      'pace_last_5',  'pace_max_5', 'pace_min_5',   'line_slope', 'line_lowOdds', 'line_highOdds',]

xgb1 = XGBClassifier(
 learning_rate =0.1,
 n_estimators=1000,
 max_depth=5,
 min_child_weight=1,
 gamma=0,
 subsample=0.8,
 colsample_bytree=0.8,
 objective= 'binary:logistic',
 nthread=4,
 scale_pos_weight=1,
 seed=27)
feat_imp= modelfit(xgb1, train, test, predictors,target,metric = 'auc')

#Grid seach on subsample and max_features
#Choose all predictors except target & IDcols
param_test1 = {
    'max_depth':range(2,10,2),
    'min_child_weight':range(1,6,2)
}
gsearch1 = GridSearchCV(estimator = XGBClassifier( learning_rate =0.1, n_estimators=140, max_depth=3,
                                        min_child_weight=8, gamma=0, colsample_bytree=0.8,subsample=0.9,
                                        objective= 'binary:logistic', nthread=4, scale_pos_weight=1, seed=27),
                       param_grid = param_test1, scoring= 'roc_auc' ,n_jobs=1,iid=False, cv=5)
gsearch1.fit(train[predictors],train[target])


print("Grid scores on development set:")
print()
means = gsearch1.cv_results_['mean_test_score']
stds = gsearch1.cv_results_['std_test_score']
for mean, std, params in zip(means, stds, gsearch1.cv_results_['params']):
    print("%0.3f (+/-%0.03f) for %r"
          % (mean, std * 2, params))
gsearch1.best_params_, gsearch1.best_score_

param_test2 = {
 'max_depth':[7,8,9,10],
 'min_child_weight':[3,4,5,6,7]
}
gsearch2 = GridSearchCV(estimator = XGBClassifier( learning_rate=0.1, n_estimators=140, max_depth=6,
 min_child_weight=4, gamma=0, subsample=0.8, colsample_bytree=0.9,
 objective= 'binary:logistic', nthread=4, scale_pos_weight=1,seed=27),
 param_grid = param_test2, scoring='roc_auc',n_jobs=1,iid=False, cv=5)
gsearch2.fit(train[predictors],train[target])
print("Grid scores on development set:")
print()
means = gsearch2.cv_results_['mean_test_score']
stds = gsearch2.cv_results_['std_test_score']
for mean, std, params in zip(means, stds, gsearch2.cv_results_['params']):
    print("%0.3f (+/-%0.03f) for %r"
          % (mean, std * 2, params))
gsearch2.best_params_, gsearch2.best_score_

param_test3 = {
 'gamma':[i/10.0 for i in range(0,5)]
}

gsearch3 = GridSearchCV(estimator = XGBClassifier( learning_rate=0.1, n_estimators=140, max_depth=10,
 min_child_weight=5, gamma=0, subsample=0.8, colsample_bytree=0.9,
 objective= 'binary:logistic', nthread=4, scale_pos_weight=1,seed=27),
 param_grid = param_test3, scoring='roc_auc',n_jobs=1,iid=False, cv=5)
gsearch3.fit(train[predictors],train[target])
print("Grid scores on development set:")
print()
means = gsearch3.cv_results_['mean_test_score']
stds = gsearch3.cv_results_['std_test_score']
for mean, std, params in zip(means, stds, gsearch3.cv_results_['params']):
    print("%0.3f (+/-%0.03f) for %r"
          % (mean, std * 2, params))
gsearch3.best_params_, gsearch3.best_score_


xgb2 = XGBClassifier(
 learning_rate =0.01,
 n_estimators=9,
 max_depth=6,
 min_child_weight=4,
 gamma=0.2,
 subsample=0.8,
 colsample_bytree=0.9,
 objective= 'binary:logistic',
 nthread=4,
 scale_pos_weight=1,
 seed=27)
modelfit(xgb2, train, test, predictors,target,metric = 'auc')


param_test4 = {
 'subsample':[i/10.0 for i in range(3,10)],
 'colsample_bytree':[i/10.0 for i in range(3,10)]
}
gsearch4 = GridSearchCV(estimator = XGBClassifier( learning_rate =0.1, n_estimators=140, max_depth=10,
 min_child_weight=5, gamma=0.3, colsample_bytree=0.8, subsample=0.9,
 objective= 'binary:logistic', nthread=4, scale_pos_weight=1,seed=27),
 param_grid = param_test4, scoring='roc_auc',n_jobs=1,iid=False, cv=5)
gsearch4.fit(train[predictors],train[target])
print("Grid scores on development set:")
print()
means = gsearch4.cv_results_['mean_test_score']
stds = gsearch4.cv_results_['std_test_score']
for mean, std, params in zip(means, stds, gsearch4.cv_results_['params']):
    print("%0.3f (+/-%0.03f) for %r"
          % (mean, std * 2, params))
gsearch4.best_params_, gsearch4.best_score_

param_test5 = {
 'colsample_bytree':[i/100.0 for i in range(15,75,5)],
'subsample':[i / 100.0 for i in range(15, 65, 5)],
}
gsearch5 = GridSearchCV(estimator = XGBClassifier( learning_rate =0.01, n_estimators=21, max_depth=2,
 min_child_weight=7, gamma=0, subsample=0.8, colsample_bytree=0.8,
 objective= 'binary:logistic', nthread=4, scale_pos_weight=1,seed=27),
 param_grid = param_test5, scoring='roc_auc',n_jobs=1,iid=False, cv=5)
gsearch5.fit(train[predictors],train[target])

print("Grid scores on development set:")
print()
means = gsearch5.cv_results_['mean_test_score']
stds = gsearch5.cv_results_['std_test_score']
for mean, std, params in zip(means, stds, gsearch5.cv_results_['params']):
    print("%0.3f (+/-%0.03f) for %r"
          % (mean, std * 2, params))
gsearch5.best_params_, gsearch5.best_score_

param_test6 = {
 'reg_alpha':[0,1e-5, 1e-2, 0.1, 1, 100]
}
gsearch6 = GridSearchCV(estimator = XGBClassifier( learning_rate =0.1, n_estimators=140, max_depth=10,
 min_child_weight=5, gamma=0.3, colsample_bytree=0.7, subsample=0.7,
 objective= 'binary:logistic', nthread=4, scale_pos_weight=1,seed=27),
 param_grid = param_test6, scoring='roc_auc',n_jobs=1,iid=False, cv=5)
gsearch6.fit(train[predictors],train[target])
print("Grid scores on development set:")
print()
means = gsearch6.cv_results_['mean_test_score']
stds = gsearch6.cv_results_['std_test_score']
for mean, std, params in zip(means, stds, gsearch6.cv_results_['params']):
    print("%0.3f (+/-%0.03f) for %r"
          % (mean, std * 2, params))
gsearch6.best_params_, gsearch6.best_score_

xgb3 = XGBClassifier(
 learning_rate =0.1,
 n_estimators=1000,
 max_depth=10,
 min_child_weight=5,
 gamma=0.3,
 colsample_bytree=0.7,
 subsample=0.7,
 reg_alpha=0.0001,
 objective= 'binary:logistic',
 nthread=4,
 scale_pos_weight=1,
 seed=27)
modelfit(xgb3, train, test, predictors,target,metric = 'auc')


xgtrain = xgb.DMatrix(train[predictors].values, label=train[target].values)
xgtest = xgb.DMatrix(test[predictors].values)
xgb3.fit(train[predictors],train[target])
pred = xgb3.predict(test[predictors])
pred_proba = xgb3.predict_proba(test[predictors])
# Print model report:
print("\nModel Report")
print("Accuracy : %.4g" % metrics.accuracy_score(test[target].values, pred))
print("AUC Score (Test): %f" % metrics.roc_auc_score(test[target].values, pred))

data['pick'].sum()
data.shape
dd=np.vstack((test['pick'],pred_proba[:,1],np.transpose(pred),np.transpose(test.values)))
dd = np.transpose(dd)
proba = pd.DataFrame(dd)
import datetime
# proba = proba[proba[3]<datetime.timedelta(minutes=5)]
pick = proba[proba[1]<0.001]
pick[0].shape,proba[proba[2]==1].shape
pick[0].sum()/pick[0].shape[0]
proba[0].sum()/proba.shape[0]

train['pick'].sum(),train.shape[0]
part = proba[(proba[0]==0.5)]
part = proba[(proba[1]>0.506)]
part = proba[(proba[1]<0.5)]
part[part[2]==1].shape
part[part[2]==0].shape
test[test[target] ==1].shape
test[test[target] ==0].shape
part.describe()
print("Accuracy : %.4g" % metrics.accuracy_score(part[3].values, part[2].values))
print("AUC Score (Test): %f" % metrics.roc_auc_score(test[target].values, pred))