from sklearn import preprocessing
import numpy as np

X_train = np.array([[ 1., -1.,  2.],
                   [ 2.,  0.,  0.],
                  [ 0.,  1., -1.]])
X_scaled = preprocessing.scale(X_train)

scaler = preprocessing.StandardScaler().fit(X_train)
scaler.transform(X_train)

X_test = [[-1,1,0]]
scaler.transform(X_test)

min_max_sclar = preprocessing.MinMaxScaler()
from sklearn import svm
from sklearn import datasets
from sklearn.model_selection import cross_val_score
iris = datasets.load_iris()
clf = svm.SVC(kernel = 'linear',C=1)
scores = cross_val_score(clf,iris.data,iris.target,cv=5)



from sklearn.model_selection import cross_validate
from sklearn.metrics import recall_score

scoring  = ['precision_macro','recall_macro']

clf = svm.SVC(kernel = 'linear',C =1,random_state=0)
scores = cross_validate(clf, iris.data,iris.target,scoring=scoring,cv=5,return_train_score = False)
pass
