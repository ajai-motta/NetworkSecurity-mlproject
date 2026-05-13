import sys,os
from networksecurity.exception.exception import CustomException
from networksecurity.logging.logging import logging
from networksecurity.constants.trainig_pipeline import MODEL_FILE_NAME,SAVED_MODEL_DIR

class NetworkModel:
    def __init__(self,preposseor,model):
        try:
            self.model=model
            self.preposseor=preposseor
        except Exception as e:
            raise CustomException(e,sys)
    
    def predict(self,X):
        try:
            transformed_input=self.preposseor.transform(X)
            y_pred=self.model.predict(transformed_input)
            return y_pred
        except Exception as e:
            raise CustomException(e,sys)