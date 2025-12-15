"""
Utils Module
============

Utility functions for data extraction and loading operations.

Functions:
    - extract_from_csv: Extract data from CSV files
    - extract_from_json: Extract data from JSON files
    - extract_from_excel: Extract data from Excel files
    - load_to_csv: Save DataFrame to CSV file
    - load_to_json: Save data to JSON file

Created: Post-Phase 10 - Utility functions
"""

from datetime import datetime
import pandas as pd
import json


def extract_from_csv(file_to_process) -> pd.DataFrame:
    """
    Extract data from a CSV file.

    Args:
        file_to_process: Path to the CSV file

    Returns:
        pandas.DataFrame: DataFrame containing the CSV data
    """
    dataframe = pd.read_csv(file_to_process, sep=';')
    return dataframe


def extract_from_json(file_to_process):
    """
    Extract data from a JSON file (line-delimited JSON).

    Args:
        file_to_process: Path to the JSON file

    Returns:
        pandas.DataFrame: DataFrame containing the JSON data
    """
    dataframe = pd.read_json(file_to_process, lines=True)
    return dataframe


def extract_from_excel(file_to_process) -> pd.DataFrame:
    """
    Extract data from an Excel file.

    Args:
        file_to_process: Path to the Excel file

    Returns:
        pandas.DataFrame: DataFrame containing the Excel data
    """
    dataframe = pd.read_excel(file_to_process)
    return dataframe


def load_to_csv(targetfile, data_to_load):
    """
    Save DataFrame to a CSV file.

    Args:
        targetfile: Path to the output CSV file
        data_to_load: pandas.DataFrame to save
    """
    data_to_load.to_csv(targetfile, sep=';', encoding='utf-8', index=False)


def load_to_json(targetfile, data_to_load):
    """
    Save data to a JSON file.

    Args:
        targetfile: Path to the output JSON file
        data_to_load: Data object to save (must be JSON serializable)

    Returns:
        Result of json.dump operation
    """
    with open(targetfile, 'w') as file:
        return json.dump(data_to_load, file)
