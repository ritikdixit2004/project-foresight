"""
Project FORESIGHT — Planning Dashboard
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Project FORESIGHT", layout="wide")

# ---------- Load Data ----------
@st.cache_data
def load_data():
    master = pd.read_csv('data/processed/master_sales.csv')
    forecast = pd.read_csv('data/processed/forecast_results.csv')
    risk = pd.read_csv('data/processed/risk_scores.csv')
    master['date'] = pd.to_datetime(master['date'])
    forecast['date'] = pd.to_datetime(forecast['date'])
    return master, forecast, risk

master, forecast, risk = load_data()

# ---------- Header ----------
st.title("📦 Project FORESIGHT")
st.caption("Demand & Inventory Intelligence — NorthBay Living")

# ---------- Sidebar Filters ----------
st.sidebar.header("Filters")
categories = ["All"] + sorted(master['category'].dropna().unique().tolist())
selected_category = st.sidebar.selectbox("Category", categories)

if selected_category != "All":
    master_f = master[master['category'] == selected_category]
    risk_f = risk[risk['category'] == selected_category]
else:
    master_f = master
    risk_f = risk

# ---------- Top KPIs ----------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue", f"₹{master_f['revenue'].sum()/1e6:,.1f}M")
col2.metric("Total Units Sold", f"{master_f['units_sold'].sum():,.0f}")
col3.metric("SKUs Needing Reorder", f"{(risk_f['risk_category']=='Reorder Now').sum()}")
col4.metric("Inventory Value at Risk", f"₹{risk_f['inventory_value_at_stake'].sum()/1e6:,.1f}M")

st.divider()

# ---------- Tabs ----------
tab1, tab2, tab3 = st.tabs(["📈 Sales Overview", "🔮 Forecast", "⚠️ Risk & Reorder"])

with tab1:
    st.subheader("Monthly Revenue Trend")
    monthly = master_f.copy()
    monthly['month'] = monthly['date'].dt.to_period('M').astype(str)
    monthly_rev = monthly.groupby('month')['revenue'].sum() / 1e6
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(monthly_rev.index, monthly_rev.values, marker='o', color='#4B3F91')
    ax.set_ylabel("Revenue (₹M)")
    plt.xticks(rotation=90)
    st.pyplot(fig)

    st.subheader("Top 10 Products by Revenue")
    top_products = master_f.groupby('product_name')['revenue'].sum().sort_values(ascending=False).head(10) / 1e6
    fig2, ax2 = plt.subplots(figsize=(10, 4))
    ax2.barh(top_products.index[::-1], top_products.values[::-1], color='#2E8B57')
    ax2.set_xlabel("Revenue (₹M)")
    st.pyplot(fig2)

with tab2:
    st.subheader("Forecast vs Actual (Sample SKU)")
    sku_list = sorted(forecast['sku_id'].unique().tolist())
    selected_sku = st.selectbox("Select SKU", sku_list)
    sku_data = forecast[forecast['sku_id'] == selected_sku].sort_values('date')
    fig3, ax3 = plt.subplots(figsize=(10, 4))
    ax3.plot(sku_data['date'], sku_data['units_sold'], label='Actual', color='black')
    ax3.plot(sku_data['date'], sku_data['forecast'], label='Forecast', color='#4B3F91', linestyle='--')
    ax3.legend()
    ax3.set_ylabel("Units Sold")
    st.pyplot(fig3)
    st.caption("Model WAPE: 24.93% (beats seasonal-naive baseline of 31.21% by 20.1%)")

with tab3:
    st.subheader("Risk & Reorder Recommendations")
    risk_counts = risk_f['risk_category'].value_counts()
    fig4, ax4 = plt.subplots(figsize=(6, 4))
    colors = {'Healthy': '#2E8B57', 'Reorder Now': '#DC2626', 'Markdown / Clear': '#7C3AED', 'Watch / Volatile': '#D97706'}
    bar_colors = [colors.get(c, 'gray') for c in risk_counts.index]
    ax4.bar(risk_counts.index, risk_counts.values, color=bar_colors)
    st.pyplot(fig4)

    st.subheader("Prioritized Action List")
    priority = risk_f[risk_f['risk_category'].isin(['Reorder Now', 'Markdown / Clear'])].sort_values(
        'inventory_value_at_stake', ascending=False)
    st.dataframe(priority, width='stretch')