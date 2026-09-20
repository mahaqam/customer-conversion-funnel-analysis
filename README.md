# Customer Conversion Funnel & Behaviour Analysis

Product analytics project built around the public **eCommerce Behavior Data from Multi-Category Store** dataset. It analyzes event-level customer behaviour across product views, carts and purchases.

## Questions
- How many unique users reach each funnel stage?
- Where does the largest drop-off occur?
- Which categories have stronger view-to-purchase conversion?
- Which sessions show cart activity but no purchase?
- How does purchasing activity change over time?

## Dataset
Download a monthly CSV from Kaggle's **eCommerce Behavior Data from Multi-Category Store** dataset and save it under `data/raw/`. Raw data is excluded from Git because the source files are large.

Expected fields include `event_time`, `event_type`, `product_id`, `category_id`, `category_code`, `brand`, `price`, `user_id`, and `user_session`.

## Run
```bash
python -m venv .venv
pip install -r requirements.txt
python src/funnel_analysis.py --input data/raw/2019-Oct.csv
```

Generated outputs include funnel KPIs, category conversion, session metrics, daily purchaser counts and a funnel chart.

## SQL
`sql/funnel_analysis.sql` contains PostgreSQL-style queries for user-stage and category conversion analysis.

## Portfolio note
The code is reproducible against the public source data. Results should only be quoted on a resume after running the analysis on the downloaded dataset.
