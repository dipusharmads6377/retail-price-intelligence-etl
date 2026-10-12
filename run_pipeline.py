from pathlib import Path
import json
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
RAW_FILE = ROOT / "data" / "raw" / "global_retail_prices_dataset.csv"
OUT = ROOT / "outputs"
CHARTS = OUT / "charts"
DB_FILE = OUT / "retail_prices.db"

TEXT_COLS = [
    "product_code", "product_name", "brand", "category", "currency",
    "store_name", "city", "country_code"
]

def extract(path=RAW_FILE):
    """Extract raw CSV into a DataFrame."""
    return pd.read_csv(path, dtype={"product_code": "string", "country_code": "string"})

def transform(raw):
    """Clean columns and values; return clean rows plus a quality report."""
    df = raw.copy()
    df.columns = [c.strip().lower() for c in df.columns]
    expected = [
        "price_record_id", "product_code", "product_name", "brand", "category",
        "price", "currency", "price_is_discounted", "store_name", "city",
        "country_code", "date_recorded"
    ]
    missing_columns = sorted(set(expected) - set(df.columns))
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    input_rows = int(len(df))
    df["price_record_id"] = pd.to_numeric(df["price_record_id"], errors="coerce")
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["date_recorded"] = pd.to_datetime(df["date_recorded"], errors="coerce")
    for col in TEXT_COLS:
        df[col] = df[col].astype("string").str.strip()
        df[col] = df[col].replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})

    # Normalize boolean values where possible without inventing unknown values.
    bool_map = {
        True: True, False: False, "True": True, "False": False,
        "true": True, "false": False, "1": True, "0": False, 1: True, 0: False
    }
    df["price_is_discounted"] = df["price_is_discounted"].map(bool_map).astype("boolean")

    duplicate_id_rows = int(df["price_record_id"].duplicated(keep="first").sum())
    df = df.drop_duplicates(subset=["price_record_id"], keep="first")
    missing_id_rows = int(df["price_record_id"].isna().sum())
    invalid_price_rows = int((df["price"].isna() | (df["price"] <= 0)).sum())
    invalid_date_rows = int(df["date_recorded"].isna().sum())

    # Analytical fact table requires valid record ID, positive price, currency, and date.
    valid = (
        df["price_record_id"].notna()
        & df["price"].notna()
        & (df["price"] > 0)
        & df["currency"].notna()
        & df["date_recorded"].notna()
    )
    clean = df.loc[valid].copy()
    clean["price_record_id"] = clean["price_record_id"].astype("int64")
    clean["price_is_discounted"] = clean["price_is_discounted"].astype("boolean")
    clean["record_month"] = clean["date_recorded"].dt.to_period("M").astype("string")
    clean["date_recorded"] = clean["date_recorded"].dt.strftime("%Y-%m-%d")

    report = {
        "input_rows": input_rows,
        "rows_after_deduplicating_record_id": int(len(df)),
        "duplicate_record_id_rows_removed": duplicate_id_rows,
        "rows_missing_record_id_after_deduplication": missing_id_rows,
        "rows_with_missing_or_nonpositive_price": invalid_price_rows,
        "rows_with_invalid_date": invalid_date_rows,
        "valid_rows_loaded": int(len(clean)),
        "rows_excluded_from_fact_table": int(input_rows - len(clean)),
        "missing_values_by_column_before_filtering": {
            col: int(raw[col].isna().sum()) for col in raw.columns
        }
    }
    return clean, report

def create_summaries(df):
    """Build analysis-ready summary DataFrames. Prices are not currency-converted."""
    d = df.copy()
    d["price"] = pd.to_numeric(d["price"], errors="coerce")
    by_currency = d.groupby("currency", dropna=False).agg(
        observations=("price_record_id", "count"),
        average_price=("price", "mean"),
        median_price=("price", "median"),
        min_price=("price", "min"),
        max_price=("price", "max")
    ).reset_index().sort_values("observations", ascending=False)
    by_country = d.groupby("country_code", dropna=False).agg(
        observations=("price_record_id", "count"),
        average_price=("price", "mean"),
        median_price=("price", "median")
    ).reset_index().sort_values("observations", ascending=False)
    by_category = d.groupby("category", dropna=False).agg(
        observations=("price_record_id", "count"),
        average_price=("price", "mean"),
        median_price=("price", "median")
    ).reset_index().sort_values("observations", ascending=False)
    monthly = d.groupby("record_month", dropna=False).agg(
        observations=("price_record_id", "count")
    ).reset_index().sort_values("record_month")
    return {
        "summary_by_currency": by_currency,
        "summary_by_country": by_country,
        "summary_by_category": by_category,
        "monthly_observations": monthly
    }

def write_charts(summaries):
    CHARTS.mkdir(parents=True, exist_ok=True)
    cur = summaries["summary_by_currency"].head(10).dropna(subset=["currency"])
    if not cur.empty:
        plt.figure(figsize=(10, 5))
        plt.bar(cur["currency"].astype(str), cur["observations"])
        plt.title("Retail Price Observations by Currency (Top 10)")
        plt.xlabel("Currency")
        plt.ylabel("Observation count")
        plt.tight_layout()
        plt.savefig(CHARTS / "observations_by_currency.png", dpi=150)
        plt.close()

    monthly = summaries["monthly_observations"].dropna(subset=["record_month"])
    if not monthly.empty:
        plt.figure(figsize=(10, 5))
        plt.plot(monthly["record_month"].astype(str), monthly["observations"], marker="o")
        plt.title("Retail Price Observations by Month")
        plt.xlabel("Recording month")
        plt.ylabel("Observation count")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(CHARTS / "monthly_observations.png", dpi=150)
        plt.close()

def load_to_sqlite(df, summaries):
    OUT.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_FILE) as conn:
        df.to_sql("fact_retail_prices", conn, if_exists="replace", index=False)
        for name, table in summaries.items():
            table.to_sql(name, conn, if_exists="replace", index=False)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_fact_date ON fact_retail_prices(date_recorded)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_fact_currency ON fact_retail_prices(currency)")
        conn.commit()

def run_pipeline():
    OUT.mkdir(parents=True, exist_ok=True)
    raw = extract()
    clean, report = transform(raw)
    summaries = create_summaries(clean)
    clean.to_csv(OUT / "clean_retail_prices.csv", index=False)
    for name, table in summaries.items():
        table.to_csv(OUT / f"{name}.csv", index=False)
    with open(OUT / "quality_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    load_to_sqlite(clean, summaries)
    write_charts(summaries)
    print("Pipeline completed.")
    print(json.dumps(report, indent=2))
    print(f"SQLite database: {DB_FILE}")
    print(f"Outputs folder: {OUT}")

if __name__ == "__main__":
    run_pipeline()
