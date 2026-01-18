from config.setting import PRODUCT_PATH, REQRUITMENT_PATH, LOAD_DATA
from scripts.extract import extract_product, extract_reqruitment
from scripts.transform import transform_product, transform_requirements
from scripts.load import load_data
import pandas as pd

# Proses Extract Data Product

# Extract
product_df = extract_product(PRODUCT_PATH)

# Transform
df = transform_product(product_df)

# Load
load_data(df, LOAD_DATA, "transformed_product.csv")

# Proses Extract Data Reqruitment

# Extract
reqruitment_df = extract_reqruitment(REQRUITMENT_PATH)

# Transform
df_req = transform_requirements(reqruitment_df)

# Load

load_data(df_req, LOAD_DATA, "transformed_requitment.csv")
