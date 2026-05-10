import os
import sys
import pandas as pd
from dotenv import load_dotenv
import numpy as np


ARTIFACT_DIR : str= "Artifacts"
SCHEMA_FILE_PATH=os.path.join("data_schema","schema.yml")
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
""""""
DATA_VALIDATION_DIR_NAME :str="data_validation"
DATA_VALIDATION_VALID_DIR:str="validated"
DATA_VALIDATION_INVALID_DIR:str="invalid"
DATA_VALIDATION_DRIFT_REPORT_DIR:str="drift_report"
DATA_VALIDATION_DRIFT_REPORT_FILE_NAME:str="report.yml"