import yaml
from networksecurity.logging.logger import logging
from networksecurity.exception.exception import NetworkSecurityException
import os,sys
import numpy as np
import dill
from sklearn.model_selection import GridSearchCV
from sklearn. metrics import r2_score
from networksecurity.utils.ml_utils.metric.classification_metric import get_classification_score
import pickle

def read_yaml_file(file_path:str)->dict:
    try:
        with open(file_path,"rb") as yaml_file:
            return yaml.safe_load(yaml_file)
    except Exception as e:
        raise NetworkSecurityException(e,sys)
    
    
def write_yaml_file(
    file_path: str,
    content: object,
    replace: bool = False
) -> None:

    try:
        if replace and os.path.exists(file_path):
            os.remove(file_path)

        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w") as file:
            yaml.dump(content, file)

    except Exception as e:
        raise NetworkSecurityException(e, sys)
    
    
def save_numpy_array(filepath:str, array:np.array):
    try:
        dir_path=os.path.dirname(filepath)
        os.makedirs(dir_path,exist_ok=True)
        with open(filepath,"wb") as file_obj:
            np.save(file_obj,array)
    except Exception as e:
        raise NetworkSecurityException(e,sys)


def save_object(filepath:str, obj:object):
    try:
        logging.info("Entered the same_object method of MainUtils class")
        os.makedirs(os.path.dirname(filepath),exist_ok=True)
        with open(filepath,"wb") as file_obj:
            pickle.dump(obj,file_obj)
        logging.info("Exited the save_object method of MainUtils class")
    except Exception as e:
        raise NetworkSecurityException(e,sys) from e
    
def load_object(filepath:str)->object:
    try:
        if not os.path.exists(filepath):
            raise Exception(f"The file: {filepath} does not exists")
        
        with open(filepath,"rb") as file_obj:
            return pickle.load(file_obj)
    except Exception as e:
        raise NetworkSecurityException(e,sys)
    
def load_numpy_array_data(filepath:str)->np.array:
    try:
        with open(filepath,"rb") as file_obj:
            return np.load(file_obj)
    except Exception as e:
        raise NetworkSecurityException(e,sys)
    
def evaluate_models(X_train, y_train, X_test, y_test, models, param):
    try:
        print("INSIDE evaluate_models")
        print("PARAM TYPE:", type(param))
        print("PARAM VALUE:", param)

        report = {}

        for model_name, model in models.items():

            para = param[model_name]

            gs = GridSearchCV(
                model,
                para,
                cv=3,
                n_jobs=-1
            )

            gs.fit(X_train, y_train)

            model.set_params(**gs.best_params_)
            model.fit(X_train, y_train)

            y_train_pred = model.predict(X_train)
            y_test_pred = model.predict(X_test)

            train_model_score = r2_score(
                y_train,
                y_train_pred
            )

            test_model_score = r2_score(
                y_test,
                y_test_pred
            )

            report[model_name] = test_model_score

        return report

    except Exception as e:
        raise NetworkSecurityException(e, sys)