from config.setting import PRODUCT_PATH, REQRUITMENT_PATH, LOAD_DATA
from scripts.extract import extract_product, extract_reqruitment
from scripts.transform import transform_product, transform_requirements
from scripts.load import load_data
import pandas as pd


# Extract Data Product
# product_df = extract_product(PRODUCT_PATH)

# Transform Data
# df = transform_product(product_df)

# Load Data ke folder
# load_data(df, LOAD_DATA, "transformed_product.csv")

# Extract Data Product
reqruitment_df = extract_reqruitment(REQRUITMENT_PATH)

# Transform Data
# df_req = transform_requirements(reqruitment_df)

# Load Data ke folder
# load_data(df_req, LOAD_DATA, "transformed_requitment.csv")

df = pd.read_csv("output/transformed_requuitment.csv")
print(df.info())
