"""
Project FORESIGHT — Planning Dashboard (Expanded)
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Project FORESIGHT", layout="wide", page_icon="📦")

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
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Revenue", f"₹{master_f['revenue'].sum()/1e6:,.1f}M")
col2.metric("Total Units Sold", f"{master_f['units_sold'].sum():,.0f}")
col3.metric("Gross Margin", f"₹{(master_f['units_sold']*master_f['gross_margin_per_unit']).sum()/1e6:,.1f}M")
col4.metric("SKUs Needing Reorder", f"{(risk_f['risk_category']=='Reorder Now').sum()}")
col5.metric("Inventory Value at Risk", f"₹{risk_f['inventory_value_at_stake'].sum()/1e6:,.1f}M")

st.divider()

# ---------- Tabs ----------
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📈 Sales Overview", "🏷️ Category Performance", "📦 Inventory Health",
    "⚠️ Stock Risk & Overstock", "🎯 Promotion Analysis", "🌦️ Seasonality",
    "🔮 Forecast & Recommendation"
])

# ===== TAB 1: SALES OVERVIEW =====
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

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Top 10 Products by Revenue")
        top_products = master_f.groupby('product_name')['revenue'].sum().sort_values(ascending=False).head(10) / 1e6
        fig2, ax2 = plt.subplots(figsize=(6, 5))
        ax2.barh(top_products.index[::-1], top_products.values[::-1], color='#2E8B57')
        ax2.set_xlabel("Revenue (₹M)")
        st.pyplot(fig2)
    with col_b:
        st.subheader("Bottom 10 Products by Revenue")
        bottom_products = master_f.groupby('product_name')['revenue'].sum().sort_values().head(10) / 1e6
        fig2b, ax2b = plt.subplots(figsize=(6, 5))
        ax2b.barh(bottom_products.index[::-1], bottom_products.values[::-1], color='#DC2626')
        ax2b.set_xlabel("Revenue (₹M)")
        st.pyplot(fig2b)

# ===== TAB 2: CATEGORY PERFORMANCE =====
with tab2:
    st.subheader("Revenue by Category")
    cat_rev = master_f.groupby('category')['revenue'].sum().sort_values(ascending=False) / 1e6
    fig3, ax3 = plt.subplots(figsize=(8, 4))
    bars = ax3.bar(cat_rev.index, cat_rev.values, color='#4B3F91')
    for bar in bars:
        h = bar.get_height()
        ax3.annotate(f'{h:.0f}M', xy=(bar.get_x()+bar.get_width()/2, h), xytext=(0,3),
                     textcoords="offset points", ha='center', fontsize=9)
    st.pyplot(fig3)

    st.subheader("Units Sold by Category")
    cat_units = master_f.groupby('category')['units_sold'].sum().sort_values(ascending=False)
    fig4, ax4 = plt.subplots(figsize=(8, 4))
    ax4.bar(cat_units.index, cat_units.values, color='#D97706')
    st.pyplot(fig4)

    st.subheader("Category Summary Table")
    cat_summary = master_f.groupby('category').agg(
        total_revenue=('revenue', 'sum'),
        total_units=('units_sold', 'sum'),
        avg_price=('unit_price', 'mean')
    ).round(2).sort_values('total_revenue', ascending=False)
    st.dataframe(cat_summary, width='stretch')

# ===== TAB 3: INVENTORY HEALTH =====
with tab3:
    st.subheader("Current Stock by Category")
    inv_by_cat = risk_f.groupby('category')['on_hand_units'].sum().sort_values(ascending=False)
    fig5, ax5 = plt.subplots(figsize=(8, 4))
    ax5.bar(inv_by_cat.index, inv_by_cat.values, color='#0EA5E9')
    ax5.set_ylabel("On-Hand Units")
    st.pyplot(fig5)

    st.subheader("Days of Cover by SKU (Top 15 Lowest — At Risk)")
    low_cover = risk_f.nsmallest(15, 'days_of_cover')[['sku_id', 'product_name', 'category', 'days_of_cover', 'on_hand_units']]
    st.dataframe(low_cover, width='stretch')

    st.subheader("Total Inventory Value")
    st.metric("Inventory Value", f"₹{risk_f['inventory_value_at_stake'].sum()/1e6:,.2f}M")

# ===== TAB 4: STOCK RISK & OVERSTOCK =====
with tab4:
    st.subheader("Risk Category Distribution")
    risk_counts = risk_f['risk_category'].value_counts()
    colors = {'Healthy': '#2E8B57', 'Reorder Now': '#DC2626',
              'Markdown / Clear': '#7C3AED', 'Watch / Volatile': '#D97706'}
    bar_colors = [colors.get(c, 'gray') for c in risk_counts.index]
    fig6, ax6 = plt.subplots(figsize=(6, 4))
    ax6.bar(risk_counts.index, risk_counts.values, color=bar_colors)
    st.pyplot(fig6)

    col_c, col_d = st.columns(2)
    with col_c:
        st.subheader("🔴 Reorder Now — Urgent")
        reorder = risk_f[risk_f['risk_category'] == 'Reorder Now'].sort_values('days_of_cover')
        st.dataframe(reorder[['sku_id', 'product_name', 'days_of_cover', 'inventory_value_at_stake']], width='stretch')
    with col_d:
        st.subheader("🟣 Overstock / Markdown Candidates")
        overstock = risk_f[risk_f['risk_category'] == 'Markdown / Clear'].sort_values(
            'inventory_value_at_stake', ascending=False)
        st.dataframe(overstock[['sku_id', 'product_name', 'days_of_cover', 'inventory_value_at_stake']], width='stretch')

# ===== TAB 5: PROMOTION ANALYSIS =====
with tab5:
    st.subheader("Promotion Impact on Units Sold")
    promo_avg = master_f.groupby('promo_flag')['units_sold'].mean()
    promo_avg.index = ['No Promotion', 'Promotion']
    fig7, ax7 = plt.subplots(figsize=(6, 4))
    ax7.bar(promo_avg.index, promo_avg.values, color=['#94A3B8', '#4B3F91'])
    ax7.set_ylabel("Avg Units Sold / Day")
    st.pyplot(fig7)

    uplift = (promo_avg['Promotion'] - promo_avg['No Promotion']) / promo_avg['No Promotion'] * 100
    st.metric("Promotion Uplift", f"{uplift:.1f}%")

    st.subheader("Revenue Generated During Promotions")
    promo_rev = master_f[master_f['promo_flag'] == 1]['revenue'].sum() / 1e6
    st.metric("Promo Revenue", f"₹{promo_rev:,.1f}M")

# ===== TAB 6: SEASONALITY =====
with tab6:
    st.subheader("Revenue by Season")
    season_order = ['Winter', 'Spring', 'Summer', 'Monsoon', 'Autumn']
    season_rev = master_f.groupby('season')['revenue'].sum().reindex(season_order) / 1e6
    fig8, ax8 = plt.subplots(figsize=(8, 4))
    ax8.bar(season_rev.index, season_rev.values, color='#D97706')
    st.pyplot(fig8)

    st.subheader("Holiday vs Non-Holiday Average Daily Sales")
    hol = master_f.copy()
    hol['is_holiday_flag'] = hol['holiday'] != 'No Holiday'
    hol_avg = hol.groupby('is_holiday_flag')['units_sold'].mean()
    hol_avg.index = ['Non-Holiday', 'Holiday']
    fig9, ax9 = plt.subplots(figsize=(6, 4))
    ax9.bar(hol_avg.index, hol_avg.values, color=['#94A3B8', '#DC2626'])
    st.pyplot(fig9)

# ===== TAB 7: FORECAST & RECOMMENDATION =====
with tab7:
    st.subheader("Forecast vs Actual (Select SKU)")
    sku_list = sorted(forecast['sku_id'].unique().tolist())
    selected_sku = st.selectbox("Select SKU", sku_list)
    sku_data = forecast[forecast['sku_id'] == selected_sku].sort_values('date')
    fig10, ax10 = plt.subplots(figsize=(10, 4))
    ax10.plot(sku_data['date'], sku_data['units_sold'], label='Actual', color='black')
    ax10.plot(sku_data['date'], sku_data['forecast'], label='Forecast', color='#4B3F91', linestyle='--')
    ax10.legend()
    ax10.set_ylabel("Units Sold")
    st.pyplot(fig10)
    st.caption("Model WAPE: 24.93% (beats seasonal-naive baseline of 31.21% by 20.1%)")

    st.subheader("📋 Prioritized Action List")
    priority = risk_f[risk_f['risk_category'].isin(['Reorder Now', 'Markdown / Clear'])].sort_values(
        'inventory_value_at_stake', ascending=False)
    st.dataframe(priority, width='stretch')