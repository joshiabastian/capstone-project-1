import pandas as pd
from glob import glob


def extract_product(folder_path):
    files = glob(f"{folder_path}/*.csv")
    dfs = [pd.read_csv(file) for file in files]
    return pd.concat(dfs, ignore_index=True)


def extract_reqrutment(file_path):
    return pd.read_csv(file_path)
