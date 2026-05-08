import os
import sys
import json 
from dotenv import load_dotenv
import psycopg2
from networksecurity.exception.exception import CustomException
import pandas as pd
import numpy as np
from networksecurity.logging.logging import logging

from networksecurity.entity.config_entity import DataIngestionConfig,TraingPipelineConfig
from networksecurity.entity.atifact_entity import DataIngetionArtifact
from sklearn.model_selection import train_test_split
from networksecurity.utils.sql_related import connect_to_postgres

class DataIngection:
    def __init__(self,data_ingesion_config:DataIngestionConfig):
        try:
            self.data_ingesion_config=data_ingesion_config
        except Exception as e:
            raise CustomException(e,sys)
    
    def export_data_as_dataframe(self):
        """
        This function returns Data after data is retuved from postgress
        """
        try:
            conn=connect_to_postgres()
            query = "SELECT * FROM phishing_data"
            #cur = conn.cursor()cur.execute("SELECT * FROM phishing_data")rows = cur.fetchall() is replaced with
            df=pd.read_sql(query,conn)
            print(df.columns)
            df.replace({"na":np.nan},inplace=True)
            return df
        except Exception as e:
            raise CustomException(e,sys)
    def export_data_into_featurestore(self,dataframe: pd.DataFrame):
        try:
            feature_store_file_path=self.data_ingesion_config.feature_store_file_path
            dir_path=os.path.dirname(feature_store_file_path)
            os.makedirs(dir_path,exist_ok=True)
            dataframe.to_csv(feature_store_file_path,index=False,header=True)
            return dataframe
        except Exception as e:
            raise CustomException(e,sys)
        

    def initate_dataingetion(self):
        try:
            dataframe=self.export_data_as_dataframe()
            dataframe2=self.export_data_into_featurestore(dataframe=dataframe)
            self.train_test_split_save(dataframe)
            dataingesionartifact=DataIngetionArtifact(self.data_ingesion_config.training_file_path,self.data_ingesion_config.testing_file_path)
            return dataingesionartifact
        except Exception as e:
            raise CustomException(e,sys)
        

    def train_test_split_save(self,dataframe):
        try:
            train_set,test_set=train_test_split(dataframe,test_size=self.data_ingesion_config.train_test_split_ratio)
            train_set: pd.DataFrame
            test_set: pd.DataFrame
            logging.info("Performed train test split")
            dir_path=os.path.dirname(self.data_ingesion_config.training_file_path)
            os.makedirs(dir_path,exist_ok=True)
            train_set.to_csv(self.data_ingesion_config.training_file_path)
            test_set.to_csv(self.data_ingesion_config.testing_file_path)
            logging.info("sucessfully completed saving tein and test csv")
        except Exception as e:
            raise CustomException(e,sys) #



