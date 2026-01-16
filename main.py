from config.setting import PRODUCT_PATH, REQRUITMENT_PATH, LOAD_DATA
from scripts.extract import extract_product, extract_reqruitment
from scripts.transform import transform_product
from scripts.load import load_data

# Extract Data Product
product_df = extract_product(PRODUCT_PATH)

# reqruitment_df = extract_reqruitment(REQRUITMENT_PATH)
# print(reqruitment_df)

# Transform Data
df = transform_product(product_df)

# Load Data ke folder
load_data(df, LOAD_DATA, "transformed_product.csv")
