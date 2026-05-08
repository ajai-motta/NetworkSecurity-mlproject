import os
import sys
from networksecurity.components.data_ingetion import DataIngection
from networksecurity.exception.exception import CustomException
from networksecurity.logging.logging import logging
from networksecurity.entity.config_entity import TraingPipelineConfig,DataIngestionConfig
if __name__ == "__main__":
    obj00=TraingPipelineConfig()
    obj0=DataIngestionConfig(training_pipeline_config=obj00)
    obj1=DataIngection(data_ingesion_config=obj0)
   
    obj1.initate_dataingetion()
