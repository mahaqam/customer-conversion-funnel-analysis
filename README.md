# Customer Conversion Funnel & Behaviour Analysis

Product analytics project using the public **Retailrocket recommender system dataset**. The event log contains real customer behaviour across product `view`, `addtocart`, and `transaction` events.

## Dataset

The analysis uses `events.csv` from the Retailrocket dataset. The uploaded file contains **2,756,101 events** from **1,407,580 unique visitors** spanning May to September 2015.

Columns used:
- `timestamp`
- `visitorid`
- `event`
- `itemid`
- `transactionid`

## Business questions

- How many visitors progress from view → add to cart → transaction?
- Where is the largest funnel drop-off?
- What proportion of cart users ultimately transact?
- Which items convert more strongly from view to transaction?
- Which visitors show high intent without completing a transaction?

## Observed results

Using sequential first-event logic so each stage must occur after the previous one:

| Stage | Unique visitors | Rate from view |
|---|---:|---:|
| View | 1,404,179 | 100.00% |
| Add to cart | 32,272 | 2.30% |
| Transaction | 9,682 | 0.69% |

The observed **cart-to-transaction conversion rate is 30.00%**. The largest drop-off occurs between product viewing and adding an item to cart.

The raw event counts are 2,664,312 views, 69,332 add-to-cart events, and 22,457 transaction events.

## Run locally

```bash
python -m venv .venv
pip install -r requirements.txt
python src/funnel_analysis.py --input data/raw/events.csv
```

Generated outputs include funnel KPIs, item-level conversion, high-intent visitor flags, daily purchaser counts, and a funnel chart.

## SQL

`sql/funnel_analysis.sql` contains PostgreSQL-style queries implementing the same sequential funnel logic and item-level conversion analysis.

## Repository results

`results/funnel_summary.csv` contains the observed funnel results calculated from the real dataset.
