# Retail Price Intelligence & ETL Pipeline

An end-to-end portfolio project that ingests retail price observations from CSV, validates and cleans the data with Python/Pandas, loads analytical tables into SQLite, and produces SQL-driven summaries and charts.

## Why this project
This project demonstrates practical skills relevant to entry-level Data Analyst and Data Engineer roles:
- Python and Pandas for ingestion, cleaning, validation, and transformation
- ETL workflow with separate extract, transform, and load steps
- SQLite data warehouse-style analytical tables
- SQL aggregations for retail price reporting
- Data quality checks and reproducible outputs
- GitHub-ready documentation and charts

## Dataset
The input file is `data/raw/global_retail_prices_dataset.csv`. It contains crowdsourced retail price observations and fields such as product, brand, category, price, currency, store, country code, and recording date. The dataset and accompanying documentation were supplied with this project.

**Important interpretation note:** prices are stored in local currencies. This project does not convert currencies, so prices across different currencies must not be compared directly. Missing fields in the supplied data are handled explicitly rather than silently fabricated.

## Pipeline
1. **Extract** — read the raw CSV.
2. **Transform** — standardize text fields, parse numeric prices and dates, remove duplicate record IDs, and flag rows with missing/invalid key values.
3. **Load** — write clean records and summary tables to `outputs/retail_prices.db`.
4. **Analyze** — run SQL aggregations by currency, country, category, store, and month.
5. **Visualize** — save charts to `outputs/charts/`.

## Quick start
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
python src/run_pipeline.py
```

After running, review:
- `outputs/quality_report.json`
- `outputs/summary_by_currency.csv`
- `outputs/summary_by_country.csv`
- `outputs/summary_by_category.csv`
- `outputs/monthly_observations.csv`
- `outputs/retail_prices.db`
- `outputs/charts/`

## SQLite tables
- `fact_retail_prices` — cleaned observation-level data
- `summary_by_currency` — observation counts and price statistics by currency
- `summary_by_country` — observation counts and price statistics by country code
- `summary_by_category` — observation counts and price statistics by category
- `monthly_observations` — observation counts over recording month

## Data quality rules
- `price_record_id` is treated as the observation identifier; duplicate IDs are reduced to one record.
- `price` must be numeric and greater than zero to be retained in the analytical fact table.
- `date_recorded` is parsed as a date; invalid dates are reported.
- Missing product names, brands, categories, store names, and locations are retained as nulls and counted in the quality report.
- Currency is preserved as provided. No currency conversion or inflation adjustment is performed.
- Extreme prices are not automatically deleted because they may reflect different products, package sizes, or local currencies.

## Project structure
```text
retail_price_intelligence_etl/
├── data/raw/                 # Original input dataset
├── src/run_pipeline.py       # ETL + SQL summaries + charts
├── tests/test_pipeline.py    # Basic transformation tests
├── outputs/                  # Generated after running pipeline
├── requirements.txt
├── .gitignore
└── README.md
```

## Limitations
- This is a batch pipeline over a static CSV snapshot, not a live production pipeline.
- There is no currency normalization, product matching, or unit-price normalization.
- Results describe the supplied snapshot only and should not be interpreted as a formal inflation index.
- Some geographic/product metadata may be missing in the source.

## Resume-ready project entry
**Retail Price Intelligence & ETL Pipeline | Python, Pandas, SQL, SQLite, Matplotlib**
- Built a reproducible ETL pipeline to ingest, clean, validate, and load retail price observations into SQLite.
- Created SQL aggregation tables for price statistics by currency, country, category, and month.
- Implemented data-quality reporting for duplicates, missing values, invalid prices, and date parsing.
- Generated visual summaries to support exploratory analysis of retail price observations.

Only include quantified results after running the pipeline and confirming the generated quality report. Do not claim cloud orchestration, Airflow, Spark, or production deployment unless you separately implement them.
