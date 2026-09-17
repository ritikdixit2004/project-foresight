# Project FORESIGHT — Demand & Inventory Intelligence

🔗 **Live Dashboard:** [Click here to view](https://project-foresight-9qzed7nexfyxcqgkjui7ay.streamlit.app)

AI-powered demand forecasting and inventory intelligence platform built for a simulated client engagement (NorthBay Living, a D2C home & lifestyle brand) as part of the Zidio Data Science & Analytics internship.

## Problem

NorthBay Living plans inventory on gut feel and spreadsheets. This causes two costly problems at once:
- **Stockouts** — best-selling products run out, resulting in lost sales.
- **Overstock** — slow-moving products pile up, locking up working capital.

This project builds a system that forecasts weekly demand per SKU, flags stockout/overstock risk, and presents it through an interactive dashboard.

## Key Results

| Metric | Value |
|---|---|
| Baseline (Seasonal-Naive) WAPE | 31.21% |
| LightGBM Model WAPE | 24.93% |
| Improvement over baseline | 20.1% |
| Total inventory value at risk identified | ₹9.57 Crore |
| SKUs flagged for reorder | 5 |
| SKUs flagged for markdown/clearance | 6 |

## Tech Stack

- **Language:** Python (pandas, numpy)
- **Modelling:** scikit-learn, LightGBM
- **Dashboard:** Streamlit
- **Deployment:** Streamlit Community Cloud

## Project Structure

## Setup & Run

```bash
# create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# install dependencies
pip install -r requirements.txt

# run the data cleaning pipeline
python src/pipeline.py

# run feature engineering
python src/features.py

# run the baseline and ML forecasting models
python src/baseline.py
python src/forecast_model.py

# run risk scoring
python src/risk_scoring.py

# launch the dashboard
streamlit run app/dashboard.py
```

## Data

Four raw extracts are provided (deliberately imperfect, simulating a real client data extract):

| File | Description |
|---|---|
| `sales_daily.csv` | Daily units sold, revenue, price, and promotion flag per SKU |
| `sku_master.csv` | Product-level details: category, cost, selling price, launch date |
| `calendar.csv` | Date attributes: week, season, holidays, promotion events |
| `inventory_snapshots.csv` | Stock position: on-hand units, lead time, reorder point |

**Key data-quality finding:** `inventory_snapshots.csv` contains 200 SKUs, but only 50 of those have matching sales and product records. This is handled in the cleaning pipeline by flagging inventory-only SKUs (`has_sales_history` column) rather than dropping them. Cleaning also fixed 36,150 missing calendar entries (non-holiday/non-promotion days).

## Methodology

1. **Data pipeline** — ingests and cleans the 4 raw extracts into one analysis-ready dataset.
2. **EDA** — identified top/bottom performing products, category trends, seasonality, and promotion impact.
3. **Feature engineering** — lag features (1/7/14/28 days), rolling averages, and calendar features, all computed using only past data (no leakage).
4. **Baseline model** — seasonal-naive forecast (WAPE 31.21%) as the benchmark.
5. **ML model** — LightGBM regressor, backtested on the last 8 weeks of data, achieving WAPE 24.93% (a 20.1% improvement over baseline).
6. **Risk scoring** — combines forecast demand with current inventory position to flag stockout risk, overstock risk, and recommended actions per SKU.
7. **Dashboard** — interactive Streamlit app with Sales, Category, Inventory, Stock Risk, Promotion, Seasonality, and Forecast views.

## Key Business Insights

1. Home Decor is the strongest revenue-driving category; Lighting is the weakest.
2. Winter is the peak sales season; Autumn is the weakest.
3. Promotions increase average daily sales by ~38%.
4. 5 SKUs are at immediate risk of stockout, with some down to 2-7 days of cover.
5. 6 SKUs are overstocked, representing capital that could be freed up through markdown/clearance.

## Roadmap

- [x] Project setup & environment
- [x] Data profiling & cleaning pipeline
- [x] Exploratory Data Analysis (EDA) with charts
- [x] Feature engineering
- [x] Baseline + ML demand forecasting model (backtested)
- [x] Stockout/overstock risk scoring
- [x] Streamlit dashboard
- [x] Deployment (Streamlit Community Cloud)
- [ ] Executive readout & final documentation