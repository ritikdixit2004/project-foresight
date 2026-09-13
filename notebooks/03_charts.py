"""
Project FORESIGHT — EDA Charts

"""
import pandas as pd
import matplotlib.pyplot as plt

master = pd.read_csv('data/processed/master_sales.csv')
master['date'] = pd.to_datetime(master['date'])

plt.style.use('seaborn-v0_8-whitegrid')

# ---------- Chart 1: Monthly Revenue Trend ----------
master['month'] = master['date'].dt.to_period('M').astype(str)
monthly_revenue = master.groupby('month')['revenue'].sum() / 1e6  # in millions

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(monthly_revenue.index, monthly_revenue.values, marker='o', color='#4B3F91', linewidth=2)
ax.set_title('Monthly Revenue Trend (2024-2025)', fontsize=14, fontweight='bold')
ax.set_xlabel('Month')
ax.set_ylabel('Revenue (₹ Millions)')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig('reports/figures/01_monthly_revenue_trend.png', dpi=150)
plt.close()
print("Saved: 01_monthly_revenue_trend.png")

# ---------- Chart 2: Revenue by Category ----------
cat_revenue = master.groupby('category')['revenue'].sum().sort_values(ascending=False) / 1e6

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(cat_revenue.index, cat_revenue.values, color='#4B3F91')
ax.set_title('Total Revenue by Category', fontsize=14, fontweight='bold')
ax.set_xlabel('Category')
ax.set_ylabel('Revenue (₹ Millions)')
for bar in bars:
    height = bar.get_height()
    ax.annotate(f'{height:.0f}M', xy=(bar.get_x() + bar.get_width()/2, height),
                xytext=(0, 3), textcoords="offset points", ha='center', fontsize=9)
plt.tight_layout()
plt.savefig('reports/figures/02_revenue_by_category.png', dpi=150)
plt.close()
print("Saved: 02_revenue_by_category.png")

# ---------- Chart 3: Top 10 Products by Revenue ----------
top_products = master.groupby('product_name')['revenue'].sum().sort_values(ascending=False).head(10) / 1e6

fig, ax = plt.subplots(figsize=(10, 6))
ax.barh(top_products.index[::-1], top_products.values[::-1], color='#2E8B57')
ax.set_title('Top 10 Products by Revenue', fontsize=14, fontweight='bold')
ax.set_xlabel('Revenue (₹ Millions)')
plt.tight_layout()
plt.savefig('reports/figures/03_top10_products.png', dpi=150)
plt.close()
print("Saved: 03_top10_products.png")

# ---------- Chart 4: Revenue by Season ----------
season_order = ['Winter', 'Spring', 'Summer', 'Monsoon', 'Autumn']
season_revenue = master.groupby('season')['revenue'].sum().reindex(season_order) / 1e6

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(season_revenue.index, season_revenue.values, color='#D97706')
ax.set_title('Revenue by Season', fontsize=14, fontweight='bold')
ax.set_xlabel('Season')
ax.set_ylabel('Revenue (₹ Millions)')
for bar in bars:
    height = bar.get_height()
    ax.annotate(f'{height:.0f}M', xy=(bar.get_x() + bar.get_width()/2, height),
                xytext=(0, 3), textcoords="offset points", ha='center', fontsize=9)
plt.tight_layout()
plt.savefig('reports/figures/04_revenue_by_season.png', dpi=150)
plt.close()
print("Saved: 04_revenue_by_season.png")

print("\nAll charts saved in reports/figures/")