from networksecurity.entity.config_entity import DataIngestionConfig,TraingPipelineConfig,DataValidationConfig,DataTransformationConfig
from networksecurity.entity.atifact_entity import DataIngetionArtifact,DataValidationArtifact,DataTransformationArtifact
from networksecurity.utils.read_write import read_yaml,write_yaml,save_numpy_array,save_object_pkl
import os 
import sys
from networksecurity.logging.logging import logging
from networksecurity.exception.exception import CustomException
from networksecurity.constants.trainig_pipeline import TARGET_COLUMN,DATA_TRANSFORMATION_IMPUTER_PARAMS
import numpy as np
import pandas as pd

from sklearn.impute import KNNImputer
from sklearn.pipeline import Pipeline

class DataTrasformation:
    def __init__(self,data_validation_artifact:DataValidationArtifact,data_transformation_config:DataTransformationConfig):
        try:
            self.data_validation_artifact:DataValidationArtifact=data_validation_artifact
            self.data_transformation_config:DataTransformationConfig=data_transformation_config
        except Exception as e:
            raise CustomException(e,sys)
        
    def get_transformer_object(self)->Pipeline:
         try:
            imputer=KNNImputer(**DATA_TRANSFORMATION_IMPUTER_PARAMS)
            processor=Pipeline([("imputer",imputer)])
            return processor

         except Exception as e:
            raise CustomException(e,sys)   
    
    @staticmethod
    def read_data(file_path:str)->pd.DataFrame:
         try:
            
           
            df=pd.read_csv(file_path)
            return df
         except Exception as e:
            raise CustomException(e,sys)   

    def initate_data_transformation(self)->DataTransformationArtifact:
        try:
            logging.info("initiated data Transformation")
            train_df=self.read_data(self.data_validation_artifact.valid_train_file_path)
            test_df=self.read_data(self.data_validation_artifact.valid_test_file_path)
            #train
            input_data_train=train_df.drop(columns=[TARGET_COLUMN.casefold()],axis=1)
            output_data_train=train_df[TARGET_COLUMN.casefold()]
            output_data_train=output_data_train.replace(-1,0)
            #test
            input_data_test=test_df.drop(columns=[TARGET_COLUMN.casefold()],axis=1)
            output_data_test=test_df[TARGET_COLUMN.casefold()]
            output_data_test=output_data_test.replace(-1,0)
            preprocessor_obj=self.get_transformer_object()
            transformed_input_train=preprocessor_obj.fit_transform(input_data_train)
            transformed_output_test=preprocessor_obj.transform(input_data_test)
            train_array=np.c_[transformed_input_train,np.array(output_data_train)]
            test_array=np.c_[transformed_output_test,np.array(output_data_test)]
            save_numpy_array(self.data_transformation_config.transformed_train_file_path,train_array)
            save_numpy_array(self.data_transformation_config.transformed_test_file_path,test_array)
            save_object_pkl(self.data_transformation_config.transformed_object_file_path,preprocessor_obj)
            save_object_pkl("final_model/final_preprocessor.pkl",preprocessor_obj)
            data_transformation_artifact=DataTransformationArtifact(transformed_object_file_path=self.data_transformation_config.transformed_object_file_path,transformed_test_file_path=self.data_transformation_config.transformed_test_file_path,transformed_train_file_path=self.data_transformation_config.transformed_train_file_path)
            return data_transformation_artifact



        except Exception as e:
            raise CustomException(e,sys)