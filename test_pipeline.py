import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from run_pipeline import transform, create_summaries

def sample_data():
    return pd.DataFrame({
        "price_record_id": [1, 2, 2, 4],
        "product_code": ["a", "b", "b", "d"],
        "product_name": ["Apple", "Bread", "Bread", "Milk"],
        "brand": [None, None, None, "Brand"],
        "category": ["fruit", "bread", "bread", "dairy"],
        "price": [2.0, 1.5, 1.5, -3],
        "currency": ["EUR", "EUR", "EUR", "EUR"],
        "price_is_discounted": ["False", "True", "True", "False"],
        "store_name": ["Shop", "Shop", "Shop", "Shop"],
        "city": ["City", "City", "City", "City"],
        "country_code": ["FR", "FR", "FR", "FR"],
        "date_recorded": ["2026-01-01", "2026-01-02", "2026-01-02", "bad-date"]
    })

def test_transform_removes_duplicate_ids_and_invalid_price():
    clean, report = transform(sample_data())
    assert clean["price_record_id"].tolist() == [1, 2]
    assert report["duplicate_record_id_rows_removed"] == 1
    assert report["valid_rows_loaded"] == 2

def test_summaries_count_rows_by_currency():
    clean, _ = transform(sample_data())
    summaries = create_summaries(clean)
    assert int(summaries["summary_by_currency"]["observations"].sum()) == 2
