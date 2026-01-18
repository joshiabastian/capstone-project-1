import pandas as pd
import numpy as np
import re
from datetime import datetime


# def transform_product(df: pd.DataFrame) -> pd.DataFrame:

#     # Drop Columns Unnamed: 0
#     df = df.drop(columns=["Unnamed: 0"])

#     # --- CAST RATING & NO OF RATINGS ---
#     df["ratings"] = pd.to_numeric(df["ratings"], errors="coerce")
#     df["no_of_ratings"] = pd.to_numeric(
#         df["no_of_ratings"].str.replace(",", ""), errors="coerce"
#     )

#     # --- SPLIT PRICE & CURRENCY (overwrite kolom harga) ---
#     def extract_price(price):
#         if pd.isna(price):
#             return None, None
#         # simbol currency pertama
#         symbol_match = re.search(r"[₹$€]", str(price))
#         currency = symbol_match.group(0) if symbol_match else "UNKNOWN"
#         # angka saja
#         value_str = re.sub(r"[^0-9]", "", str(price))
#         value = int(value_str) if value_str else None
#         return value, currency

#     # discount_price
#     df[["discount_price", "discount_price_currency"]] = df["discount_price"].apply(
#         lambda x: pd.Series(extract_price(x))
#     )

#     # actual_price
#     df[["actual_price", "actual_price_currency"]] = df["actual_price"].apply(
#         lambda x: pd.Series(extract_price(x))
#     )

#     # --- DERIVE DISCOUNT ---
#     df["discount_amount"] = df["actual_price"] - df["discount_price"]
#     df["discount_percent"] = round(
#         (df["discount_amount"] / df["actual_price"]) * 100, 2
#     )

#     # --- NORMALIZE CATEGORY (overwrite) ---
#     df["main_category"] = df["main_category"].str.strip().str.title()
#     df["sub_category"] = df["sub_category"].str.strip().str.title()

#     # --- FLAG MISSING DATA ---
#     df["has_discount"] = df["discount_price"].notna()
#     df["has_rating"] = df["ratings"].notna()

#     # --- RESET INDEX DEFAULT PANDAS ---
#     df.reset_index(drop=True, inplace=True)

#     return df


def extract_price_and_currency(price_str):
    """
    Extract harga dan currency dari string price
    Input: '₹15,999', '$299', '€150'
    Output: (15999, '₹') atau (None, 'unknown')
    """
    try:
        if pd.isna(price_str) or price_str == "":
            return None, "unknown"

        price_str = str(price_str).strip()

        # Detect currency symbol
        currency_symbols = {"₹": "₹", "$": "$", "€": "€", "£": "£"}
        currency = "unknown"

        for symbol in currency_symbols:
            if symbol in price_str:
                currency = symbol
                break

        # Extract numeric value (remove all non-digits)
        value_str = re.sub(r"[^0-9]", "", price_str)
        value = int(value_str) if value_str else None

        return value, currency

    except:
        return None, "unknown"


def categorize_rating(rating):
    """
    Kategorikan rating menjadi label
    5.0-4.5: Excellent
    4.4-4.0: Very Good
    3.9-3.5: Good
    3.4-3.0: Fair
    <3.0: Poor
    """
    if pd.isna(rating):
        return "No Rating"

    if rating >= 4.5:
        return "Excellent"
    elif rating >= 4.0:
        return "Very Good"
    elif rating >= 3.5:
        return "Good"
    elif rating >= 3.0:
        return "Fair"
    else:
        return "Poor"


def categorize_price(price, quantiles):
    """
    Kategorikan harga berdasarkan quantiles
    """
    if pd.isna(price):
        return "unknown"

    q25, q50, q75 = quantiles

    if price <= q25:
        return "Budget"
    elif price <= q50:
        return "Mid-Range"
    elif price <= q75:
        return "Premium"
    else:
        return "Luxury"


def transform_product(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform product data dengan:
    1. Drop unnamed columns
    2. Parse & split price columns (value + currency)
    3. Cast ratings to numeric
    4. Calculate discount metrics
    5. Normalize categories
    6. Add enrichment columns
    7. Add data quality flags
    """
    df_transformed = df.copy()
    initial_rows = len(df_transformed)

    # --- 1. DROP UNNAMED COLUMNS ---
    unnamed_cols = [col for col in df_transformed.columns if "unnamed" in col.lower()]
    if unnamed_cols:
        df_transformed = df_transformed.drop(columns=unnamed_cols)
        print(f"✓ Dropped {len(unnamed_cols)} unnamed column(s)")

    # --- 2. PARSE & SPLIT DISCOUNT_PRICE ---
    if "discount_price" in df_transformed.columns:
        print("✓ Parsing discount_price to value + currency")

        price_data = df_transformed["discount_price"].apply(extract_price_and_currency)
        df_transformed["discount_price_value"] = price_data.apply(lambda x: x[0])
        df_transformed["discount_price_currency"] = price_data.apply(lambda x: x[1])
        df_transformed = df_transformed.drop(columns=["discount_price"])

    # --- 3. PARSE & SPLIT ACTUAL_PRICE ---
    if "actual_price" in df_transformed.columns:
        print("✓ Parsing actual_price to value + currency")

        price_data = df_transformed["actual_price"].apply(extract_price_and_currency)
        df_transformed["actual_price_value"] = price_data.apply(lambda x: x[0])
        df_transformed["actual_price_currency"] = price_data.apply(lambda x: x[1])
        df_transformed = df_transformed.drop(columns=["actual_price"])

    # --- 4. CAST RATINGS TO NUMERIC ---
    if "ratings" in df_transformed.columns:
        print("✓ Converting ratings to numeric")
        df_transformed["ratings"] = pd.to_numeric(
            df_transformed["ratings"], errors="coerce"
        )

        # Validate rating range (0-5)
        invalid_ratings = (
            df_transformed["ratings"].between(0, 5, inclusive="both") == False
        )
        if invalid_ratings.any():
            df_transformed.loc[invalid_ratings, "ratings"] = np.nan

    # --- 5. CAST NO_OF_RATINGS TO NUMERIC ---
    if "no_of_ratings" in df_transformed.columns:
        print("✓ Converting no_of_ratings to numeric")
        df_transformed["no_of_ratings"] = pd.to_numeric(
            df_transformed["no_of_ratings"].astype(str).str.replace(",", ""),
            errors="coerce",
        )

    # --- 6. CALCULATE DISCOUNT METRICS ---
    if (
        "discount_price_value" in df_transformed.columns
        and "actual_price_value" in df_transformed.columns
    ):
        print("✓ Calculating discount metrics")

        # Discount amount
        df_transformed["discount_amount"] = (
            df_transformed["actual_price_value"]
            - df_transformed["discount_price_value"]
        )

        # Discount percent
        df_transformed["discount_percent"] = round(
            (df_transformed["discount_amount"] / df_transformed["actual_price_value"])
            * 100,
            2,
        )

        # Handle invalid discounts (discount_price > actual_price)
        invalid_discount = df_transformed["discount_amount"] < 0
        if invalid_discount.any():
            df_transformed.loc[
                invalid_discount, ["discount_amount", "discount_percent"]
            ] = 0

    # --- 7. NORMALIZE CATEGORIES ---
    category_cols = ["main_category", "sub_category"]
    for col in category_cols:
        if col in df_transformed.columns:
            print(f"✓ Normalizing {col}")
            df_transformed[col] = (
                df_transformed[col]
                .astype(str)
                .str.strip()
                .str.title()
                .replace("Nan", "Unknown")
            )

    # --- 8. ADD ENRICHMENT COLUMNS ---
    print("✓ Adding enrichment columns")

    # Rating category
    if "ratings" in df_transformed.columns:
        df_transformed["rating_category"] = df_transformed["ratings"].apply(
            categorize_rating
        )

    # Price category (based on quantiles)
    if "discount_price_value" in df_transformed.columns:
        valid_prices = df_transformed["discount_price_value"].dropna()
        if len(valid_prices) > 0:
            q25 = valid_prices.quantile(0.25)
            q50 = valid_prices.quantile(0.50)
            q75 = valid_prices.quantile(0.75)
            df_transformed["price_category"] = df_transformed[
                "discount_price_value"
            ].apply(lambda x: categorize_price(x, (q25, q50, q75)))

    # Savings category
    if "discount_percent" in df_transformed.columns:
        df_transformed["savings_level"] = pd.cut(
            df_transformed["discount_percent"],
            bins=[-np.inf, 0, 10, 25, 50, np.inf],
            labels=["No Discount", "Low", "Medium", "High", "Very High"],
        )

    # --- 9. ADD DATA QUALITY FLAGS ---
    print("✓ Adding data quality flags")

    # Has discount
    if "discount_price_value" in df_transformed.columns:
        df_transformed["has_discount"] = df_transformed["discount_price_value"].notna()

    # Has rating
    if "ratings" in df_transformed.columns:
        df_transformed["has_rating"] = df_transformed["ratings"].notna()

    # Has image
    if "image" in df_transformed.columns:
        df_transformed["has_image"] = df_transformed["image"].notna() & (
            df_transformed["image"] != ""
        )

    # Data completeness score (0-100)
    required_fields = ["name", "discount_price_value", "ratings", "image"]
    existing_fields = [f for f in required_fields if f in df_transformed.columns]

    if existing_fields:
        df_transformed["completeness_score"] = (
            df_transformed[existing_fields].notna().sum(axis=1)
            / len(existing_fields)
            * 100
        ).round(0)

    # --- 10. CLEAN DATA ---
    # Remove duplicates
    duplicates = df_transformed.duplicated().sum()
    if duplicates > 0:
        df_transformed = df_transformed.drop_duplicates()
        print(f"✓ Removed {duplicates} duplicate rows")

    # Strip whitespace from text columns
    text_cols = df_transformed.select_dtypes(include=["object"]).columns
    for col in text_cols:
        df_transformed[col] = df_transformed[col].apply(
            lambda x: x.strip() if isinstance(x, str) else x
        )

    # Reset index
    df_transformed.reset_index(drop=True, inplace=True)

    # --- SUMMARY ---
    print(
        f"✓ Transform complete: {initial_rows} to {len(df_transformed)} rows, {len(df_transformed.columns)} columns"
    )

    return df_transformed


# Transform Data Requitments


def parse_datetime_column(datetime_str):
    """
    Memecah datetime string menjadi date, time, dan timezone
    Input: '2024-12-23 17:00+07:00'
    Output: date, time, timezone='Asia/Jakarta'
    """
    try:
        if pd.isna(datetime_str) or datetime_str == "":
            return pd.Series(
                {"date": np.nan, "time": np.nan, "timezone": "Asia/Jakarta"}
            )

        datetime_str = str(datetime_str).strip()

        # Extract timezone (+07:00)
        timezone_match = re.search(r"([+-]\d{2}[:.]?\d{2})$", datetime_str)

        # Remove timezone dari string
        datetime_clean = re.sub(r"[+-]\d{2}[:.]?\d{2}$", "", datetime_str).strip()

        # Parse datetime
        dt = pd.to_datetime(datetime_clean, errors="coerce")

        if pd.isna(dt):
            return pd.Series(
                {"date": np.nan, "time": np.nan, "timezone": "Asia/Jakarta"}
            )

        return pd.Series(
            {"date": dt.date(), "time": dt.time(), "timezone": "Asia/Jakarta"}
        )

    except:
        return pd.Series({"date": np.nan, "time": np.nan, "timezone": "Asia/Jakarta"})


def parse_salary(salary_str):
    """
    Memecah salary string menjadi min, max, avg, currency, dan type
    Contoh: '$50k - $80k per year', '$25 - $40 per hour', '$60,000'
    """
    try:
        if pd.isna(salary_str) or salary_str == "":
            return pd.Series(
                {
                    "salary_min": np.nan,
                    "salary_max": np.nan,
                    "salary_avg": np.nan,
                    "salary_currency": "USD",
                    "salary_type": "unknown",
                }
            )

        salary_str = str(salary_str).strip()
        currency = "USD"

        # Detect salary type (yearly/hourly/unknown)
        salary_type = "unknown"
        if re.search(
            r"(per\s+year|yearly|annual|per\s+annum|\/year)", salary_str, re.IGNORECASE
        ):
            salary_type = "yearly"
        elif re.search(r"(per\s+hour|hourly|\/hour|hr)", salary_str, re.IGNORECASE):
            salary_type = "hourly"

        # Remove currency symbols dan text
        cleaned = re.sub(
            r"(USD|\$|per|year|yearly|annual|annum|hour|hourly|hr|month|\/)",
            "",
            salary_str,
            flags=re.IGNORECASE,
        )
        cleaned = cleaned.strip()

        # Handle notasi "k" (thousand)
        if "k" in cleaned.lower():
            cleaned = re.sub(r"k", "", cleaned, flags=re.IGNORECASE)
            numbers = re.findall(r"\d+(?:[.,]\d+)?", cleaned)
            numbers = [float(n.replace(",", ".")) * 1000 for n in numbers]
        else:
            # Extract numbers
            numbers = re.findall(r"\d+(?:[.,]\d+)*", cleaned)
            numbers = [float(n.replace(",", "")) for n in numbers]

        if len(numbers) == 0:
            return pd.Series(
                {
                    "salary_min": np.nan,
                    "salary_max": np.nan,
                    "salary_avg": np.nan,
                    "salary_currency": currency,
                    "salary_type": salary_type,
                }
            )
        elif len(numbers) == 1:
            sal_min = sal_max = numbers[0]
        else:
            sal_min = min(numbers)
            sal_max = max(numbers)

        sal_avg = (sal_min + sal_max) / 2

        return pd.Series(
            {
                "salary_min": sal_min,
                "salary_max": sal_max,
                "salary_avg": sal_avg,
                "salary_currency": currency,
                "salary_type": salary_type,
            }
        )

    except:
        return pd.Series(
            {
                "salary_min": np.nan,
                "salary_max": np.nan,
                "salary_avg": np.nan,
                "salary_currency": "USD",
                "salary_type": "unknown",
            }
        )


def transform_requirements(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform data dengan:
    1. Split datetime → date, time, timezone
    2. Parse salary → min, max, avg, currency
    3. Clean whitespace
    4. Remove duplicates
    5. Handle missing values
    6. Add metadata
    """
    df_transformed = df.copy()
    initial_rows = len(df_transformed)

    # --- 1. TRANSFORM DATETIME COLUMN ---
    date_columns = [
        col
        for col in df_transformed.columns
        if "date" in col.lower() or "time" in col.lower()
    ]

    if date_columns:
        date_col = date_columns[0]
        print(f"✓ Split datetime: '{date_col}' → date, time, timezone")

        date_parts = df_transformed[date_col].apply(parse_datetime_column)
        df_transformed["date"] = date_parts["date"]
        df_transformed["time"] = date_parts["time"]
        df_transformed["timezone"] = date_parts["timezone"]
        df_transformed = df_transformed.drop(columns=[date_col])

    # --- 2. TRANSFORM SALARY COLUMN ---
    salary_columns = [
        col
        for col in df_transformed.columns
        if "salary" in col.lower() or "gaji" in col.lower()
    ]

    if salary_columns:
        salary_col = salary_columns[0]
        print(f"✓ Parse salary: '{salary_col}' → min, max, avg, currency, type")

        salary_parts = df_transformed[salary_col].apply(parse_salary)
        df_transformed["salary_min"] = salary_parts["salary_min"]
        df_transformed["salary_max"] = salary_parts["salary_max"]
        df_transformed["salary_avg"] = salary_parts["salary_avg"]
        df_transformed["salary_currency"] = salary_parts["salary_currency"]
        df_transformed["salary_type"] = salary_parts["salary_type"]
        df_transformed = df_transformed.drop(columns=[salary_col])

    # --- 3. DATA CLEANING ---
    # Clean whitespace
    for col in df_transformed.select_dtypes(include=["object"]).columns:
        df_transformed[col] = df_transformed[col].apply(
            lambda x: x.strip() if isinstance(x, str) else x
        )

    # Remove duplicates
    duplicates = df_transformed.duplicated().sum()
    if duplicates > 0:
        df_transformed = df_transformed.drop_duplicates()
        print(f"✓ Removed {duplicates} duplicate rows")

    # --- 4. HANDLE MISSING VALUES ---
    # String columns → 'Unknown'
    for col in df_transformed.select_dtypes(include=["object"]).columns:
        if col != "timezone":
            null_count = df_transformed[col].isna().sum()
            if null_count > 0:
                df_transformed[col] = df_transformed[col].fillna("Unknown")

    # Numeric columns → keep NaN

    # --- 5. OPTIMIZE DATA TYPES ---
    if "date" in df_transformed.columns:
        df_transformed["date"] = pd.to_datetime(df_transformed["date"], errors="coerce")

    print(
        f"✓ Transform complete: {initial_rows} → {len(df_transformed)} rows, {len(df_transformed.columns)} columns"
    )

    return df_transformed
