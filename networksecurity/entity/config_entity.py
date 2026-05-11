from datetime import datetime
import os
from networksecurity.constants import trainig_pipeline

class TraingPipelineConfig:
    def __init__(self,timestamp=datetime.now()):
        timestamp=timestamp.strftime("%m_%d_%Y_%H_%M_%S")
        self.timestamp=timestamp
        self.pipeline_name=trainig_pipeline.PIPELINE_NAME
        self.artifact_name=trainig_pipeline.ARTIFACT_DIR
        self.artifact_dir=os.path.join(self.artifact_name,self.timestamp)

class DataIngestionConfig:
    def __init__(self,training_pipeline_config:TraingPipelineConfig):
        self.data_ingection_dir=os.path.join(training_pipeline_config.artifact_dir,trainig_pipeline.DATA_Ingestion_DIR)
        self.feature_store_file_path=os.path.join(self.data_ingection_dir,trainig_pipeline.DATA_Ingestion_FREATURE_STORE_DIR,trainig_pipeline.FILE_NAME)
        self.training_file_path=os.path.join(self.data_ingection_dir,trainig_pipeline.DATA_Ingestion_INGESTED_DIR,trainig_pipeline.TRAIN_FILE_NAME)
        self.testing_file_path=os.path.join(self.data_ingection_dir,trainig_pipeline.DATA_Ingestion_INGESTED_DIR,trainig_pipeline.TEST_FILE_NAME)
        self.train_test_split_ratio: float=trainig_pipeline.DATA_Ingestion_TEST_RATIO
        self.database_name=trainig_pipeline.DATA_Ingestion_DTABASE_NAME
        self.database_table_name=trainig_pipeline.DATA_Ingestion_TABLE_NAME

class DataValidationConfig:
    def __init__(self,training_pipeline_config:TraingPipelineConfig):
        self.data_validation_dir=os.path.join(training_pipeline_config.artifact_dir,trainig_pipeline.DATA_VALIDATION_DIR_NAME)
        self.valid_data_dir=os.path.join(self.data_validation_dir,trainig_pipeline.DATA_VALIDATION_VALID_DIR)
        self.invalid_data_dir=os.path.join(self.data_validation_dir,trainig_pipeline.DATA_VALIDATION_INVALID_DIR)
        self.valid_train_file_path=os.path.join(self.valid_data_dir,trainig_pipeline.TRAIN_FILE_NAME)
        self.valid_test_file_path=os.path.join(self.valid_data_dir,trainig_pipeline.TEST_FILE_NAME)
        self.invalid_train_file_path=os.path.join(self.invalid_data_dir,trainig_pipeline.TRAIN_FILE_NAME)
        self.invalid_test_file_path=os.path.join(self.invalid_data_dir,trainig_pipeline.TRAIN_FILE_NAME)
        self.drift_report_file_path=os.path.join(self.data_validation_dir,trainig_pipeline.DATA_VALIDATION_DRIFT_REPORT_DIR,trainig_pipeline.DATA_VALIDATION_DRIFT_REPORT_FILE_NAME)
        
class DataTransformationConfig:
    def __init__(self,training_pipeline_config:TraingPipelineConfig):
        self.data_transformation_dir:str=os.path.join(training_pipeline_config.artifact_dir,trainig_pipeline.DATA_TRANSFORMATION_DIR_NAME)
        self.transformed_train_file_path: str=os.path.join(self.data_transformation_dir,trainig_pipeline.DATA_TRANSFORMATION_TRANSFORMED_DATA_DIR_NAME,
                                                           trainig_pipeline.TRAIN_FILE_NAME.replace("csv","npy")
                                                           )
        self.transformed_test_file_path: str=os.path.join(self.data_transformation_dir,trainig_pipeline.DATA_TRANSFORMATION_TRANSFORMED_DATA_DIR_NAME,
                                                           trainig_pipeline.TEST_FILE_NAME.replace("csv","npy"))
        self.transformed_object_file_path: str=os.path.join(self.data_transformation_dir,trainig_pipeline.DATA_TRANSFORMATION_TRANSFORMED_DATA_DIR_NAME,trainig_pipeline.DATA_TRANSFORMATION_TRANSFORMED_OBJECT_DIR_NAME,trainig_pipeline.PREPOSESSOR_FILE_NAME)