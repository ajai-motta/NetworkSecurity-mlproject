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
            columns = data["schema"]["columns"]
            print("First 3 records:\n")
            print('length is',len(data["schema"]["columns"]))
            for col in columns[:3]:
                print(col)

            return data

    except Exception as e:
        raise CustomException(e,sys)

def write_yaml(file_path: str, data: dict) -> None:
        """
        Writes a dictionary to a YAML file.
        """

        try:
            with open(file_path, "w") as file:
                yaml.dump(data, file, default_flow_style=False)

            print(f"YAML file created at: {file_path}")

        except Exception as e:
            raise CustomException(e,sys)


if __name__=="__main__":
    try:
        read_yaml(os.path.join("data_schema","schema.yml"))
    
    except Exception as e:
        raise CustomException(e,sys)