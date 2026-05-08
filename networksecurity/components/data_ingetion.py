import os
import sys
import json 
from dotenv import load_dotenv
import psycopg2
from networksecurity.exception.exception import CustomException
import pandas as pd
import numpy as np
from io import StringIO
from networksecurity.logging.logging import logging

from networksecurity.entity.config_entity import DataIngestionConfig,TraingPipelineConfig

from sklearn.model_selection import train_test_split
from networksecurity.utils.sql_related import connect_to_postgres

class DataIngection:
    def __init__(self,data_ingesion_config:DataIngestionConfig):
        try:
            self.data_ingesion_config=data_ingesion_config
        except Exception as e:
            raise CustomException(e,sys)
    
    def export_data_as_dataframe(self):
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
    
    def initate_dataingetion(self):
        try:
            dataframe=self.export_data_as_dataframe()
        except Exception as e:
            raise CustomException(e,sys)


if __name__ == "__main__":
    obj00=TraingPipelineConfig()
    obj0=DataIngestionConfig(training_pipeline_config=obj00)
    obj1=DataIngection(data_ingesion_config=obj0)
   
    obj1.initate_dataingetion()

