import sys,os
from networksecurity.exception.exception import CustomException
from networksecurity.logging.logging import logging
import yaml
import dill,pickle

def read_yaml(file_path: str) -> dict:
    """
    Reads a YAML file and returns its contents as a dictionary.
    """

    try:
        with open(file_path, "r") as file:
            data = yaml.safe_load(file)
            return data

    except Exception as e:
        raise CustomException(e,sys)