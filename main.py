from config.setting import PRODUCT_PATH, REQRUITMENT_PATH, LOAD_DATA
from scripts.extract import extract_product, extract_requirements
from scripts.transform import transform_product, transform_requirements
from scripts.load import load_data


# Proses Extract Data Product

# Extract
product_df = extract_product(PRODUCT_PATH)

# Transform
df = transform_product(product_df)

# Load
load_data(df, LOAD_DATA, "transformed_product-test.csv")

# Proses Extract Data Reqruitment

# # Extract
# reqruitment_df = extract_requirements(REQRUITMENT_PATH)

# # Transform
# df_req = transform_requirements(reqruitment_df)
# print(df_req.info())

# # Load

# load_data(df_req, LOAD_DATA, "transformed_requitment-test.csv")
