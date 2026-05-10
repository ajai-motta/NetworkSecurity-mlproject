from dataclasses import dataclass

@dataclass
class DataIngetionArtifact:
    training_file_path:str
    testing_file_path:str

@dataclass
class DataValidationArtifact:
    validation_status: bool
    valid_train_file_path: str
    valid_test_file_path: str
    invalid_train_file_path: str
    invalid_test_file_path: str
    drif_report_file_path: str

