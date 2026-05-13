import sys,os

from sklearn.metrics import f1_score, r2_score
from networksecurity.exception.exception import CustomException
from networksecurity.logging.logging import logging
import yaml
import dill,pickle
import numpy as np
from sklearn.model_selection import GridSearchCV



def evaluate_model(X_train,y_train,X_test,y_test,models,params)->dict:
    try:
       report={}
       for i in range(len(list(models))):
            model=list(models.values())[i]
            param=params[list(models.keys())[i]]
            gs=GridSearchCV(model,param,cv=3,verbose=1)
            gs.fit(X_train,y_train)
            model.set_params(**gs.best_params_)
            model.fit(X_train,y_train)
            y_train_pred=model.predict(X_train)
            y_test_pred=model.predict(X_test)
            train_f1_score=r2_score(y_train,y_train_pred)
            test_f1_score=f1_score(y_test,y_test_pred)
            report[list(models.keys())[i]]=test_f1_score
       return report
    except Exception as e:
        raise CustomException(e,sys)