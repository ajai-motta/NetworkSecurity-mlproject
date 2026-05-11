import sys,os
from networksecurity.exception.exception import CustomException
from networksecurity.logging.logging import logging
import yaml
import dill,pickle
import numpy as np

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



def save_numpy_array(file_path: str, array: np.ndarray) -> None:
    """
    Save a NumPy array to a .npy file.

    Args:
        file_path (str): Path where the file should be saved.
        array (np.ndarray): NumPy array to save.
    """
    try:
        dir_name=os.path.dirname(file_path)
        os.makedirs(dir_name,exist_ok=True)
        with open(file_path, "wb") as file:
                np.save(file, array)
                print(f"Array saved at: {file_path}")

        print(f"YAML file created at: {file_path}")

    except Exception as e:
        raise CustomException(e,sys)    

def save_object_pkl(file_path: str, obj: object) -> None:
    """
    Save a Python object as a .pkl file.

   
    """
    
    try:
        dir_name = os.path.dirname(file_path)
        os.makedirs(dir_name, exist_ok=True)

        with open(file_path, "wb") as file:
            pickle.dump(obj, file)

        print(f"Pickle file saved at: {file_path}")

    except Exception as e:
        raise CustomException(e, sys)




if __name__=="__main__":
    try:
        read_yaml(os.path.join("data_schema","schema.yml"))
    
    except Exception as e:
        raise CustomException(e,sys)