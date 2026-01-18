import pandas as pd
from glob import glob
import os

# Extract data product


def extract_product(folder_path):
    """
    Extract multiple CSV files dari folder dan gabungkan

    Args:
        folder_path (str): Path ke folder yang berisi file CSV

    Returns:
        pd.DataFrame: Gabungan semua data CSV
    """
    files = glob(f"{folder_path}/*.csv")

    if not files:
        raise FileNotFoundError(f"Tidak ada file CSV di folder: {folder_path}")

    print(f"✓ Found {len(files)} CSV file(s)")

    dfs = []
    for file in files:
        df = pd.read_csv(file)
        print(f"  - {os.path.basename(file)}: {len(df)} rows")
        dfs.append(df)

    combined_df = pd.concat(dfs, ignore_index=True)
    print(
        f"✓ Extract complete: {len(combined_df)} total rows, {len(combined_df.columns)} columns"
    )

    return combined_df


# Extract data reqruitment


def extract_requirements(file_path):
    """
    Extract/load data dari file CSV
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File tidak ditemukan: {file_path}")

    df = pd.read_csv(file_path)
    print(f"✓ Extract: {len(df)} rows, {len(df.columns)} columns")

    return df
