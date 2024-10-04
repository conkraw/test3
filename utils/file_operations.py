# utils/file_operations.py

import pandas as pd

def load_users():
    #return pd.read_csv('users.csv')
    return pd.read_csv('users.txt')
def read_text_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        return None

def load_vital_signs(file_path):
    try:
        with open(file_path, 'r') as file:
            data = file.read().splitlines()
            vital_signs = {}
            for line in data:
                if ',' in line:  # Ensure the line contains a comma
                    key, value = line.split(',', 1)  # Split only on the first comma
                    vital_signs[key.strip()] = value.strip()
            return vital_signs
    except FileNotFoundError:
        st.error(f"File not found: {file_path}")
        return {}
    except Exception as e:
        st.error(f"Error loading vital signs: {e}")
        return {}

def read_diagnoses_from_file():
    try:
        with open('dx_list.txt', 'r') as file:
            diagnoses = [line.strip() for line in file.readlines() if line.strip()]
        return diagnoses
    except Exception as e:
        st.error(f"Error reading dx_list.txt: {e}")
        return []
