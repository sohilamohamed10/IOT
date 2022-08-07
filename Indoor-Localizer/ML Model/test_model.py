from ctypes import string_at
from re import finditer
import time
import pickle
import numpy as np
import pandas as pd
from sklearn.svm import SVC
from micromlgen import port
from statistics import mode
from firebase import firebase
from sklearn.metrics import accuracy_score
from sklearn.naive_bayes import GaussianNB
from sklearn.utils import check_random_state
from sklearn.metrics import confusion_matrix
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import train_test_split






DataBase=[]
pkl_filename = "pickle_modelFINAL.pkl"
firebase = firebase.FirebaseApplication('https://task1fire-default-rtdb.firebaseio.com/', authentication=None)
def Classification():

   Wifi_1 = pd.read_csv(r'lab1.csv').iloc[:71,1:7]
   Wifi_2 = pd.read_csv(r'co1.csv').iloc[:71,1:7]
   Wifi_3 = pd.read_csv(r'co2.csv').iloc[:71,1:7]
   Wifi_4 = pd.read_csv(r'lab2.csv').iloc[:71,1:7]
       
   
   Wifi_list=[Wifi_1,Wifi_2,Wifi_3,Wifi_4]
   
   
   for wifi_indx in range(len(Wifi_list)):
   
    #Wifi_list[wifi_indx]=Wifi_list[wifi_indx].iloc[:71,1:6]
    #print(wifi_indx )
    Wifi_list[wifi_indx] = Wifi_list[wifi_indx].replace(0, -90)
    Wifi_list[wifi_indx].iloc[:,-1]=int(wifi_indx)
    
    #print(Wifi_list[wifi_indx].iloc[:,-1])
   
   
   
   wifi_data = pd.concat( Wifi_list, ignore_index=True)
   wifi_data.to_csv (r'C:\Users\DELL\Desktop\Task1\Nice\export_dataframe.csv', index = False, header=True)
   #print(list(wifi_data.iloc[:,-1]))
   
   
   
   wifi_data= wifi_data.dropna()
   print(wifi_data.shape)
   
   
   x=wifi_data.iloc[:,:-1]
   y=list(wifi_data.iloc[:,-1])
    #print(np.unique(y))
    #print(X.shape)


   # training a DescisionTreeClassifier
   #classifier = DecisionTreeClassifier(max_depth = 2).fit(X_train, y_train)


   # training a RandomForestClassifier
   #classifier =RandomForestClassifier(max_depth=None,random_state=1,max_leaf_nodes=None,min_samples_split=2).fit(x, y)
  
   # training a SVM classifier
   classifier = SVC(kernel='linear').fit(x, y)
   
    


  # training a KNeighborsClassifierclassifier
   #classifier = KNeighborsClassifier(5).fit(X_train, y_train)

   # training a GaussianNBClassifierclassifier
   #classifier = GaussianNB().fit(X_train, y_train)
   return classifier


def prediction(classifier):
    #try:
    StrengthOfWifi = []
    DataFromFireBase = firebase.get('/RSSI',None)
  
  
    for key,value in DataFromFireBase.items():
              
         trial_value=np.array(value.split()).astype('int')
         trial_value=trial_value[1:]
         StrengthOfWifi.append(trial_value)      
    print(classifier.predict(np.array(StrengthOfWifi))) 
    predict = mode(classifier.predict(np.array(StrengthOfWifi)))
   
        
    #except:
     #      pass
    return predict
    
    


def main():
    if (finditer(pkl_filename,r"C:\Users\DELL\Desktop\Task1\Nice")):
    
        with open(pkl_filename, 'rb') as file:
            #classifier=Classification()
            #pickle.dump(classifier, file)
            classifier = pickle.load(file)
            print("file is found")
    else:
        classifier = Classification()
        with open(pkl_filename, 'wb') as file:
            pickle.dump(classifier, file)
    predict=int(prediction(classifier))
    print(predict)
    
    firebase.put('','label',predict)
    return 0


if __name__ == '__main__':
    while True:
        main()

#https://github.com/eloquentarduino/micromlgen