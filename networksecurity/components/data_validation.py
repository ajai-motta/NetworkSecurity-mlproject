from networksecurity.entity.config_entity import DataIngestionConfig,TraingPipelineConfig,DataValidationConfig
from networksecurity.entity.atifact_entity import DataIngetionArtifact,DataValidationArtifact
import os 
import sys
from networksecurity.logging.logging import logging
from networksecurity.exception.exception import CustomException
from networksecurity.constants.trainig_pipeline import SCHEMA_FILE_PATH
from scipy.stats import ks_2samp
import pandas as pd


class DataValidation:
    def __init__(self,data_ingetion_artifact:DataIngetionArtifact,data_validation_config:DataValidationConfig):
        try:
            
            self.data_ingetion_artifact=data_ingetion_artifact
            self.data_validation_config=data_validation_config
            self._schema_config=read_yaml_file(SCHEMA_FILE_PATH)
        except Exception as e:
            raise CustomException(e,sys)
  