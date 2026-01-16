from config.setting import PRODUCT_PATH, REQRUITMENT_PATH
from scripts.extract import extract_product, extract_reqruitment
from scripts.transform import transform_product

product_df = extract_product(PRODUCT_PATH)

# reqruitment_df = extract_reqruitment(REQRUITMENT_PATH)
# print(reqruitment_df)

df = transform_product(product_df)
print(df.head(10))
