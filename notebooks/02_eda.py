"""
Project FORESIGHT — Exploratory Data Analysis (EDA)
Step 1: Top/bottom products, category performance, dead-stock check.

"""
import pandas as pd

master = pd.read_csv('data/processed/master_sales.csv')

print("="*60)
print("TOP 10 PRODUCTS BY TOTAL REVENUE")
print("="*60)
top_products = master.groupby('product_name')['revenue'].sum().sort_values(ascending=False).head(10)
print(top_products.round(0))

print("\n" + "="*60)
print("BOTTOM 10 PRODUCTS BY TOTAL REVENUE (possible dead stock)")
print("="*60)
bottom_products = master.groupby('product_name')['revenue'].sum().sort_values().head(10)
print(bottom_products.round(0))

print("\n" + "="*60)
print("REVENUE BY CATEGORY")
print("="*60)
cat_revenue = master.groupby('category')['revenue'].sum().sort_values(ascending=False)
print(cat_revenue.round(0))

print("\n" + "="*60)
print("TOTAL UNITS SOLD BY PRODUCT (checking for zero-sale products)")
print("="*60)
units_by_product = master.groupby('product_name')['units_sold'].sum().sort_values()
print(f"Products with ZERO total units sold: {(units_by_product == 0).sum()}")
print(units_by_product.head(5))
print("\n" + "="*60)
print("MONTHLY REVENUE TREND")
print("="*60)
master['date'] = pd.to_datetime(master['date'])
master['month'] = master['date'].dt.to_period('M')
monthly_revenue = master.groupby('month')['revenue'].sum()
print(monthly_revenue.round(0))

print("\n" + "="*60)
print("REVENUE BY SEASON")
print("="*60)
season_revenue = master.groupby('season')['revenue'].sum().sort_values(ascending=False)
print(season_revenue.round(0))

print("\n" + "="*60)
print("HOLIDAY vs NON-HOLIDAY AVERAGE DAILY SALES")
print("="*60)
master['is_holiday_flag'] = master['holiday'] != 'No Holiday'
holiday_avg = master.groupby('is_holiday_flag')['units_sold'].mean()
print(holiday_avg.round(2))

print("\n" + "="*60)
print("PROMOTION IMPACT ON UNITS SOLD")
print("="*60)
promo_avg = master.groupby('promo_flag')['units_sold'].mean()
print(promo_avg.round(2))
print("\n--- DEBUG: holiday column check (full) ---")
print("Total rows:", len(master))
print("Missing (NaN) values in holiday column:", master['holiday'].isnull().sum())
print(master['holiday'].value_counts(dropna=False))