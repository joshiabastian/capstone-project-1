import pandas as pd
import re


def transform_product(df):

    # Drop Columns Unnamed: 0
    df = df.drop(columns=["Unnamed: 0"])

    # --- CAST RATING & NO OF RATINGS ---
    df["ratings"] = pd.to_numeric(df["ratings"], errors="coerce")
    df["no_of_ratings"] = pd.to_numeric(
        df["no_of_ratings"].str.replace(",", ""), errors="coerce"
    )

    # --- SPLIT PRICE & CURRENCY (overwrite kolom harga) ---
    def extract_price(price):
        if pd.isna(price):
            return None, None
        # simbol currency pertama
        symbol_match = re.search(r"[₹$€]", str(price))
        currency = symbol_match.group(0) if symbol_match else "UNKNOWN"
        # angka saja
        value_str = re.sub(r"[^0-9]", "", str(price))
        value = int(value_str) if value_str else None
        return value, currency

    # discount_price
    df[["discount_price", "discount_price_currency"]] = df["discount_price"].apply(
        lambda x: pd.Series(extract_price(x))
    )

    # actual_price
    df[["actual_price", "actual_price_currency"]] = df["actual_price"].apply(
        lambda x: pd.Series(extract_price(x))
    )

    # --- DERIVE DISCOUNT ---
    df["discount_amount"] = df["actual_price"] - df["discount_price"]
    df["discount_percent"] = round(
        (df["discount_amount"] / df["actual_price"]) * 100, 2
    )

    # --- NORMALIZE CATEGORY (overwrite) ---
    df["main_category"] = df["main_category"].str.strip().str.title()
    df["sub_category"] = df["sub_category"].str.strip().str.title()

    # --- FLAG MISSING DATA ---
    df["has_discount"] = df["discount_price"].notna()
    df["has_rating"] = df["ratings"].notna()

    # --- RESET INDEX DEFAULT PANDAS ---
    df.reset_index(drop=True, inplace=True)

    return df
