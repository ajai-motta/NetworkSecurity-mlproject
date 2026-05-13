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

''''''''
DATA_TRANSFORMATION_DIR_NAME="data_transformation"
DATA_TRANSFORMATION_TRANSFORMED_DATA_DIR_NAME="transformed"
DATA_TRANSFORMATION_TRANSFORMED_OBJECT_DIR_NAME="transformed_object"
PREPOSESSOR_FILE_NAME='preposseor.pkl'

DATA_TRANSFORMATION_IMPUTER_PARAMS:dict={
        "missing_values": np.nan, 
        "n_neighbors":3,
        "weights": "uniform"
    }

""""model trainer"""

MODEL_TRAINER_DIR:str='model_trainer'
MODEL_FILE_NAME:str='model.pkl'
MODEL_TRAINER_TRAINED_DIR:str='trained_model'
MODEL_TRAINER_EXPECTED_SCORE:float=0.6
MODEL_OVERFITTING_THESHOLD: float=0.05
SAVED_MODEL_DIR:str="saved_models"

