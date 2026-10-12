-- Run in SQLite after `python src/run_pipeline.py`
-- 1. Observation volume by currency
SELECT currency, observations, average_price, median_price
FROM summary_by_currency
ORDER BY observations DESC;

-- 2. Most represented categories
SELECT category, observations, average_price
FROM summary_by_category
ORDER BY observations DESC
LIMIT 15;

-- 3. Monthly data coverage
SELECT record_month, observations
FROM monthly_observations
ORDER BY record_month;

-- 4. Inspect potential missing product metadata
SELECT
  COUNT(*) AS total_rows,
  SUM(CASE WHEN product_name IS NULL THEN 1 ELSE 0 END) AS missing_product_names,
  SUM(CASE WHEN brand IS NULL THEN 1 ELSE 0 END) AS missing_brands
FROM fact_retail_prices;
