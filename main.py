import os
import sys
from networksecurity.components.data_ingetion import DataIngection
from networksecurity.components.data_validation import DataValidation
from networksecurity.components.data_transformation import DataTrasformation
from networksecurity.components.model_trainer import ModelTrainer
from networksecurity.exception.exception import CustomException
from networksecurity.logging.logging import logging
from networksecurity.entity.config_entity import TraingPipelineConfig,DataIngestionConfig,DataValidationConfig,DataTransformationConfig,ModelTrainerConfig
if __name__ == "__main__":
    try:
        obj00=TraingPipelineConfig()
        obj0=DataIngestionConfig(training_pipeline_config=obj00)
        obj1=DataIngection(data_ingesion_config=obj0)
        data_indetion_artifact=obj1.initate_dataingetion()
        data_validation_config=DataValidationConfig(obj00)
        data_validation_instance=DataValidation(data_ingetion_artifact=data_indetion_artifact,data_validation_config=data_validation_config)
        data_validation_artifact=data_validation_instance.initate_data_validation()
        data_transformation_config=DataTransformationConfig(training_pipeline_config=obj00)
        data_transformation=DataTrasformation(data_validation_artifact,data_transformation_config=data_transformation_config)
        data_transformation_atrtifact=data_transformation.initate_data_transformation()
        model_trainer_config=ModelTrainerConfig(training_pipeline_config=obj00)
        model_trainer=ModelTrainer(model_trainer_config=model_trainer_config,data_transformation_artifact=data_transformation_atrtifact)
        model_trainer_artifact=model_trainer.initate_model_trainer()
    except Exception as e:
        raise CustomException(e,sys)
    


