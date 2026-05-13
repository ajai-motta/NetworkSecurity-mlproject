import sys,os
from networksecurity.exception.exception import CustomException
from networksecurity.logging.logging import logging
from sklearn.metrics import f1_score,precision_score,recall_score
from networksecurity.entity.atifact_entity import ClassificationMetricArtifact

def calculate_classification_metrics(y_true,y_pred)->ClassificationMetricArtifact:
    try:
        f1=f1_score(y_true,y_pred)
        precision=precision_score(y_true,y_pred)
        recall=recall_score(y_true,y_pred)
        classification_metric_artifact=ClassificationMetricArtifact(f1_score=f1,precision_score=precision,recall_score=recall)
        return classification_metric_artifact
    except Exception as e:
        raise CustomException(e,sys)