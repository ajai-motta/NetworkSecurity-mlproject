import os
import sys
import pandas as pd
from dotenv import load_dotenv
import numpy as np


ARTIFACT_DIR : str= "Artifacts"

TRAIN_FILE_NAME : str= "train.csv"
TEST_FILE_NAME : str= "test.csv"
PIPELINE_NAME: str= "NETWORKSECURITY"
FILE_NAME :str="phisingData.csv"
#MODEL_FILE_NAME : str = "model.pkl"

#PREPROCESSOR_FILE_NAME = "preprocessor.pkl"

TARGET_COLUMN = "Result"

DATA_Ingestion_DTABASE_NAME: str="mydb"
DATA_Ingestion_TABLE_NAME: str="phishing_data"
DATA_Ingestion_DIR: str="data_ingection"
DATA_Ingestion_FREATURE_STORE_DIR: str="feature_store"
DATA_Ingestion_INGESTED_DIR:str="ingested"
DATA_Ingestion_TEST_RATIO:float= 0.2