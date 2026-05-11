import os
import sys
from networksecurity.components.data_ingetion import DataIngection
from networksecurity.components.data_validation import DataValidation
from networksecurity.exception.exception import CustomException
from networksecurity.logging.logging import logging
from networksecurity.entity.config_entity import TraingPipelineConfig,DataIngestionConfig,DataValidationConfig
if __name__ == "__main__":
    try:
        obj00=TraingPipelineConfig()
        obj0=DataIngestionConfig(training_pipeline_config=obj00)
        obj1=DataIngection(data_ingesion_config=obj0)
        data_indetion_artifact=obj1.initate_dataingetion()
        data_validation_config=DataValidationConfig(obj00)
        data_validation_instance=DataValidation(data_ingetion_artifact=data_indetion_artifact,data_validation_config=data_validation_config)
        data_validation_artifact=data_validation_instance.initate_data_validation()
    except Exception as e:
        raise CustomException(e,sys)
    


