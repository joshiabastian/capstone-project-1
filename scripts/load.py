import pandas as pd
import os

# Load data product dan requitment


def load_data(df, folder_path=None, file_name=None):
    """
    df: DataFrame tidak boleh kosong
    folder_path: Folder tidak boleh kosong
    file_name: Isi Nama File
    """
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    df.to_csv(os.path.join(folder_path, file_name), index=False)
    print(f"Data berhasil di load!!")
