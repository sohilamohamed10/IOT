import time
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.utils import check_random_state
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import StratifiedKFold
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier


Wifi_1 = pd.read_csv(r'lab1.csv').iloc[:71,1:7]
Wifi_2 = pd.read_csv(r'co1.csv').iloc[:71,1:7]
Wifi_3 = pd.read_csv(r'co2.csv').iloc[:71,1:7]
Wifi_4 = pd.read_csv(r'lab2.csv').iloc[:71,1:7]
    

Wifi_list=[Wifi_1,Wifi_2,Wifi_3,Wifi_4]


for wifi_indx in range(len(Wifi_list)):

 #Wifi_list[wifi_indx]=Wifi_list[wifi_indx].iloc[:71,1:6]
 #print(wifi_indx )
 Wifi_list[wifi_indx].iloc[:,-1]=int(wifi_indx)
 #print(Wifi_list[wifi_indx].iloc[:,-1])



wifi_data = pd.concat( Wifi_list, ignore_index=True)
wifi_data.to_csv (r'C:\Users\DELL\Desktop\Task1\Nice\export_dataframe.csv', index = False, header=True)
#print(list(wifi_data.iloc[:,-1]))



wifi_data= wifi_data.dropna()
print(wifi_data.shape)
wifi_data = wifi_data.replace(0, -90)

x=wifi_data.iloc[:,:-1]
y=list(wifi_data.iloc[:,-1])
#print(np.unique(y))
#print(X.shape)


print(x)
# Apply the function

  


# Split to Train & Test data
X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.2 ,random_state=42)

# training a DescisionTreeClassifier
#dtree_model = DecisionTreeClassifier(max_depth = 2).fit(X_train, y_train)
#dtree_predictions = dtree_model.predict(X_test)
# Acc == 0.536


# training a RandomForestClassifier
#RF=RandomForestClassifier(max_depth=None,random_state=1,max_leaf_nodes=None,min_samples_split=2)
# create model and Test it
#RF.fit(X_train, y_train)
#RF_predictions = RF.predict(X_test)
#score = r.score(X_test, y_test)
#print("Test score with L2 penalty: %.4f" % score)
#Acc == 73.9 with random seed=60



# training a SVM classifier
SVMclassifier = SVC(kernel='linear').fit(X_train, y_train)
SVMclassifier_predictions = SVMclassifier.predict(X_test)
#Acc == 71 with random seed=42


# training a KNeighborsClassifierclassifier
#knnclassifier = KNeighborsClassifier(5).fit(X_train, y_train)
#knnclassifier_predictions = knnclassifier.predict(X_test)
#Acc == 71  with random seed=42


# training a GaussianNBClassifierclassifier
#GaussianNBClassifier = GaussianNB().fit(X_train, y_train)
#GaussianNBClassifier_predictions =GaussianNBClassifier.predict(X_test)
#Acc == 79.7 with random seed=42


print(accuracy_score(y_test,RF_predictions ))
 