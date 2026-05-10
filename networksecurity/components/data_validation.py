from networksecurity.entity.config_entity import DataIngestionConfig,TraingPipelineConfig,DataValidationConfig
from networksecurity.entity.atifact_entity import DataIngetionArtifact,DataValidationArtifact
from networksecurity.utils.read_write import read_yaml,write_yaml
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
            self._schema_config=read_yaml(SCHEMA_FILE_PATH)
        except Exception as e:
            raise CustomException(e,sys)
        


    
    @staticmethod
    def read_data(file_path:str)->pd.DataFrame:
         try:
            
           
            train_dataframe=pd.read_csv(file_path)
            return train_dataframe
         except Exception as e:
            raise CustomException(e,sys)
      

   

    def check_data_drift(self,base_df:pd.DataFrame,current_df:pd.DataFrame,threshold=0.05)->bool:
        
         try:
            status:bool=True
            report:dict={}
            is_found:bool
            for column in base_df.columns:
                d1=base_df[column]
                d2=current_df[column]
                is_sample=ks_2samp(d1,d2)
                if threshold <= is_sample.pvalue:
                    is_found=False
                else:
                    is_found=True
                    status=False
                report.update({column:{
                   "pvalue":float(is_sample.pvalue),
                   "drift_status":is_found
                }})
                dirift_file_path=self.data_validation_config.drift_report_file_path
                dir_name=os.path.dirname(dirift_file_path)
                os.makedirs(dir_name,exist_ok=True)
                write_yaml(file_path=dirift_file_path,data=report)
                return status


         except Exception as e:
            raise CustomException(e,sys)
        
    



    def validate_no_columns(self,dataframe:pd.DataFrame):
        
         try:
            
           number_of_colums_in_schema=len(self._schema_config["schema"]["columns"])
           logging.info(f"required number of columns are: {number_of_colums_in_schema}")
           if len(dataframe)==number_of_colums_in_schema:
               return True
           else:
               return False
         except Exception as e:
            raise CustomException(e,sys)
        
    def initate_data_validation(self)->DataValidationArtifact:
         try:
            error_message
            test_file_path=self.data_ingetion_artifact.testing_file_path
            train_file_path=self.data_ingetion_artifact.training_file_path
            train_dataframe=DataValidation.read_data(train_file_path)
            test_dataframe=DataValidation.read_data(test_file_path)
            status=self.validate_no_columns(dataframe=train_dataframe)
            if not status:
                error_message=f"nonumber of columns are not equal to the schema provided in train dataframe\n"
            status=self.validate_no_columns(dataframe=test_dataframe)
            if not status:
                error_message=f"nonumber of columns are not equal to the schema provided in test dataframe\n"
            #data dirft
            status=self.check_data_drift(base_df=train_dataframe,current_df=test_dataframe)
         except Exception as e:
            raise CustomException(e,sys)
  