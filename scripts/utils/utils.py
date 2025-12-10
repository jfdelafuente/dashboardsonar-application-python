from datetime import datetime
import pandas as pd
import json

def extract_from_csv(file_to_process) -> pd.DataFrame: 
    dataframe = pd.read_csv(file_to_process, sep=';') 
    return dataframe

def extract_from_json(file_to_process):
    dataframe = pd.read_json(file_to_process, lines=True)
    return dataframe

def extract_from_excel(file_to_process) -> pd.DataFrame:
    dataframe = pd.read_excel(file_to_process) 
    return dataframe

def load_to_csv(targetfile, data_to_load):
    data_to_load.to_csv(targetfile, sep=';', encoding='utf-8', index=False)
    
def load_to_json(targetfile, data_to_load):
    with open(targetfile, 'w') as file:
        return json.dump(data_to_load, file)