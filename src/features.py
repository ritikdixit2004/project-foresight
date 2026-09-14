"""
Project FORESIGHT — Feature Engineering
Builds lag, rolling, and calendar features for the demand forecasting model.
"""
import pandas as pd

def build_features(master):
    df = master.copy()
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(['sku_id', 'date'])

    # Lag features: units sold N days ago (only past data)
    for lag in [1, 7, 14, 28]:
        df[f'lag_{lag}'] = df.groupby('sku_id')['units_sold'].shift(lag)

    # Rolling averages: average of the past N days (shifted by 1 to avoid leakage)
    for window in [7, 14, 28]:
        df[f'rolling_mean_{window}'] = (
            df.groupby('sku_id')['units_sold']
              .shift(1)
              .rolling(window)
              .mean()
              .reset_index(level=0, drop=True)
        )

    # Calendar features
    df['day_of_week'] = df['date'].dt.dayofweek  # 0=Monday, 6=Sunday
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    df['month_num'] = df['date'].dt.month
    df['is_holiday_flag'] = (df['holiday'] != 'No Holiday').astype(int)

    return df

if __name__ == "__main__":
    master = pd.read_csv('data/processed/master_sales.csv')
    featured = build_features(master)

    # Drop rows where lag features are NaN (start of each SKU's history)
    before = len(featured)
    featured_clean = featured.dropna(subset=['lag_28', 'rolling_mean_28'])
    after = len(featured_clean)

    featured_clean.to_csv('data/processed/features.csv', index=False)

    print(f"Total rows before dropping early NaN rows: {before}")
    print(f"Total rows after: {after} (dropped {before - after} rows with insufficient history)")
    print(f"New feature columns: {[c for c in featured_clean.columns if c not in master.columns]}")
    print("\nSample row:")
    print(featured_clean[['date', 'sku_id', 'units_sold', 'lag_1', 'lag_7',
                           'rolling_mean_7', 'is_weekend', 'is_holiday_flag']].head(3))