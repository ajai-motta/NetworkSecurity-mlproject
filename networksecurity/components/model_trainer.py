from networksecurity.entity.config_entity import DataValidationConfig,DataTransformationConfig,ModelTrainerConfig
from networksecurity.entity.atifact_entity import DataTransformationArtifact,ModelTrainerArtifact,ClassificationMetricArtifact
from networksecurity.utils.read_write import read_yaml,write_yaml,save_numpy_array,save_object_pkl,load_numpy_object
from networksecurity.utils.model import evaluate_model
from networksecurity.utils.classification_metric import calculate_classification_metrics
import os 
import sys
from networksecurity.logging.logging import logging
from networksecurity.exception.exception import CustomException
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import GradientBoostingRegressor,AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import r2_score
import numpy as np
import pandas as pd
import mlflow

class ModelTrainer:
    def __init__(self,model_trainer_config:ModelTrainerConfig,data_transformation_artifact:DataTransformationArtifact):
        try:
            self.model_trainer_config=model_trainer_config
            self.data_transformation_artifact=data_transformation_artifact
        except Exception as e:
            raise CustomException(e,sys)
    

    def mlflow_func(self,best_model,classification_metric_artifact_train:ClassificationMetricArtifact,classification_metric_test:ClassificationMetricArtifact):
        try:
            logging.info("Starting MLflow tracking setup")
            mlflow.set_tracking_uri("file:./mlruns")
            logging.info("MLflow tracking URI set to file:./mlruns")
            
            mlflow.set_experiment("Network_Security_Experiment")
            logging.info("MLflow experiment set to 'Network_Security_Experiment'")
            
            with mlflow.start_run(run_name="Model_Training_Run"):
                logging.info("MLflow run started with name 'Model_Training_Run'")
                
                model_name = best_model.__class__.__name__
                mlflow.log_param("model_name", model_name)
                logging.info(f"Logged parameter - model_name: {model_name}")
                
                mlflow.log_metric("train_f1_score", classification_metric_artifact_train.f1_score)
                mlflow.log_metric("train_precision", classification_metric_artifact_train.precision_score)
                mlflow.log_metric("train_recall", classification_metric_artifact_train.recall_score)
                logging.info(f"Logged training metrics - F1: {classification_metric_artifact_train.f1_score}, Precision: {classification_metric_artifact_train.precision_score}, Recall: {classification_metric_artifact_train.recall_score}")
                
                mlflow.log_metric("test_f1_score", classification_metric_test.f1_score)
                mlflow.log_metric("test_precision", classification_metric_test.precision_score)
                mlflow.log_metric("test_recall", classification_metric_test.recall_score)
                logging.info(f"Logged test metrics - F1: {classification_metric_test.f1_score}, Precision: {classification_metric_test.precision_score}, Recall: {classification_metric_test.recall_score}")
                
                mlflow.sklearn.log_model(best_model, "model")
                logging.info("Model logged to MLflow successfully")
        except Exception as e:
            logging.error(f"Error in MLflow tracking: {str(e)}")
            raise CustomException(e,sys)
    def train_model(self,x_train,y_train,x_test,y_test):
        try:
            logging.info("Started model training process")
            logging.info(f"Training data shape: {x_train.shape}, Test data shape: {x_test.shape}")
            
            models={
                "RandomForestClassifier":RandomForestClassifier(),
                "GradientBoostingClassifier":GradientBoostingClassifier(),
                "AdaBoostClassifier":AdaBoostClassifier(),
                "DecisionTreeClassifier":DecisionTreeClassifier(),
                "KNeighborsClassifier":KNeighborsClassifier(),
                "LogisticRegression":LogisticRegression()
                }
            params={
                "RandomForestClassifier":{
                    'n_estimators': [100, 200],
                    'max_depth': [None, 10, 20],
                    'min_samples_split': [2, 5],
                    'min_samples_leaf': [1, 2]
                },
                "GradientBoostingClassifier":{
                    'n_estimators': [100, 200],
                    'learning_rate': [0.01, 0.1],
                    'max_depth': [3, 5]
                },
                "AdaBoostClassifier":{
                    'n_estimators': [50, 100],
                    'learning_rate': [0.01, 0.1]
                },
                "DecisionTreeClassifier":{
                    'max_depth': [None, 10, 20],
                    'min_samples_split': [2, 5],
                    'min_samples_leaf': [1, 2]
                },
                "KNeighborsClassifier":{
                    'n_neighbors': [3, 5, 7],
                    'weights': ['uniform', 'distance']
                },
                "LogisticRegression":{
                    'C': [0.1, 1.0, 10.0],
                    'penalty': ['l1', 'l2']
                }
            }
            model_report:dict=evaluate_model(X_train=x_train,y_train=y_train,X_test=x_test,y_test=y_test,models=models,params=params)
            logging.info(f"Model evaluation completed. Model scores: {model_report}")
            
            best_model_name = max(model_report, key=model_report.get)
            best_model_score = model_report[best_model_name] # why does auto complete sort the dict values in ascending order
            best_model=models[best_model_name]
            logging.info(f"Best model selected: {best_model_name} with F1 score of {best_model_score}")
            best_model=models[best_model_name]
            logging.info("Training best model on full training dataset")
            best_model.fit(x_train,y_train)
            logging.info("Model training completed successfully")
            
            logging.info("Making predictions on training and test sets")
            y_train_pred=best_model.predict(x_train)
            y_test_pred=best_model.predict(x_test)
            logging.info("Predictions generated for both training and test sets")
            
            logging.info("Calculating classification metrics")
            classification_metric_artifact_train=calculate_classification_metrics(y_train,y_train_pred)
            classification_metric_test=calculate_classification_metrics(y_test,y_test_pred)
            logging.info(f"Training metrics - F1: {classification_metric_artifact_train.f1_score}, Precision: {classification_metric_artifact_train.precision_score}, Recall: {classification_metric_artifact_train.recall_score}")
            logging.info(f"Test metrics - F1: {classification_metric_test.f1_score}, Precision: {classification_metric_test.precision_score}, Recall: {classification_metric_test.recall_score}")
            
            logging.info(f"Saving trained model to {self.model_trainer_config.trained_model_file_name}")
            save_object_pkl(self.model_trainer_config.trained_model_file_name,best_model)
            # for final model saving
            save_object_pkl("final_model/final_model.pkl",best_model)

            logging.info("Model saved successfully")
            
            model_trainer_artifact=ModelTrainerArtifact(model_file_path=self.model_trainer_config.trained_model_file_name,train_metric_artifact=classification_metric_artifact_train,test_metric_artifact=classification_metric_test)
            logging.info("Calling MLflow function to log metrics and model")
            self.mlflow_func(best_model,classification_metric_artifact_train,classification_metric_test)
            logging.info("Model training pipeline completed successfully")
            return model_trainer_artifact


        except Exception as e:
            raise CustomException(e,sys)
        
    def initate_model_trainer(self)->ModelTrainerArtifact:
         try:
            logging.info("Initiated model trainer")
            logging.info(f"Loading transformed training data from {self.data_transformation_artifact.transformed_train_file_path}")
            train_file_path=self.data_transformation_artifact.transformed_train_file_path
            test_file_path=self.data_transformation_artifact.transformed_test_file_path
            train_array=load_numpy_object(train_file_path)
            test_array=load_numpy_object(test_file_path)
            logging.info(f"Data loaded successfully - Train shape: {train_array.shape}, Test shape: {test_array.shape}")
            
            logging.info("Splitting data into features and target")
            x_train,y_train=train_array[:,:-1],train_array[:,-1]
            x_test,y_test=test_array[:,:-1],test_array[:,-1]
            logging.info(f"Data split completed - X_train: {x_train.shape}, y_train: {y_train.shape}, X_test: {x_test.shape}, y_test: {y_test.shape}")
            
            logging.info("Starting model training process")
            model_trainer_artifact=self.train_model(x_train,y_train,x_test,y_test)
            logging.info("Model training completed, returning artifact")
            return model_trainer_artifact
         except Exception as e:
            logging.error(f"Error in model trainer: {str(e)}")
            raise CustomException(e,sys)