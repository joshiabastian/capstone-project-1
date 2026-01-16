from config.setting import PRODUCT_PATH, REQRUITMENT_PATH
from scripts.extract import extract_product, extract_reqruitment

product_df = extract_product(PRODUCT_PATH)
print(product_df)

# reqruitment_df = extract_reqruitment(REQRUITMENT_PATH)
# print(reqruitment_df)
