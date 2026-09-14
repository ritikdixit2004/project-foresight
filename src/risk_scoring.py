"""
Project FORESIGHT — Stockout & Overstock Risk Scoring
"""
import pandas as pd
import numpy as np

if __name__ == "__main__":
    forecast = pd.read_csv('data/processed/forecast_results.csv')
    inventory = pd.read_csv('data/processed/inventory_clean.csv')
    sku_master = pd.read_csv('data/processed/sku_master_clean.csv')

    forecast['date'] = pd.to_datetime(forecast['date'])
    inventory['date'] = pd.to_datetime(inventory['date'])

    # Average daily forecasted demand per SKU (over the test/forecast horizon)
    avg_daily_forecast = forecast.groupby('sku_id')['forecast'].mean().reset_index()
    avg_daily_forecast.columns = ['sku_id', 'avg_daily_demand']

    # Latest inventory snapshot per SKU
    latest_inventory = inventory.sort_values('date').groupby('sku_id').tail(1)

    # Merge forecast + inventory + product info
    risk_df = avg_daily_forecast.merge(latest_inventory, on='sku_id', how='inner')
    risk_df = risk_df.merge(sku_master[['sku_id', 'product_name', 'category', 'list_price']],
                             on='sku_id', how='left')

    # Demand over the lead time (how much will sell before a new order arrives)
    risk_df['demand_over_lead_time'] = risk_df['avg_daily_demand'] * risk_df['lead_time_days']
    risk_df['available_stock'] = risk_df['on_hand_units'] + risk_df['on_order_units']

    # Days of cover: how many days will current stock last at current demand
    risk_df['days_of_cover'] = np.where(
        risk_df['avg_daily_demand'] > 0,
        risk_df['on_hand_units'] / risk_df['avg_daily_demand'],
        999
    )

    # Stockout risk: will stock run out before lead time covers it?
    risk_df['stockout_risk'] = risk_df['available_stock'] < risk_df['demand_over_lead_time']

    # Overstock risk: on-hand stock covers more than 60 days of demand
    risk_df['overstock_risk'] = risk_df['days_of_cover'] > 60

    def classify(row):
        if row['stockout_risk'] and not row['overstock_risk']:
            return 'Reorder Now'
        elif row['overstock_risk'] and not row['stockout_risk']:
            return 'Markdown / Clear'
        elif row['stockout_risk'] and row['overstock_risk']:
            return 'Watch / Volatile'
        else:
            return 'Healthy'

    risk_df['risk_category'] = risk_df.apply(classify, axis=1)

    # Rupee value at stake
    risk_df['inventory_value_at_stake'] = risk_df['on_hand_units'] * risk_df['list_price']

    # Save output
    output_cols = ['sku_id', 'product_name', 'category', 'on_hand_units', 'avg_daily_demand',
                   'days_of_cover', 'lead_time_days', 'risk_category', 'inventory_value_at_stake']
    risk_df[output_cols].to_csv('data/processed/risk_scores.csv', index=False)

    print("RISK CATEGORY SUMMARY:")
    print(risk_df['risk_category'].value_counts())

    print(f"\nTotal inventory value at stake: ₹{risk_df['inventory_value_at_stake'].sum():,.0f}")

    print("\n--- Sample: Reorder Now SKUs ---")
    reorder = risk_df[risk_df['risk_category'] == 'Reorder Now'][output_cols].head(5)
    print(reorder.to_string(index=False))

    print("\nSaved: data/processed/risk_scores.csv")