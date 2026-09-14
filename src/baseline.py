"""
Project FORESIGHT — Baseline Forecast Model
Seasonal-naive baseline: predicts this week's demand = same period last week.
"""
import pandas as pd
import numpy as np

def wape(actual, predicted):
    """Weighted Absolute Percentage Error — robust to low-volume SKUs."""
    return np.sum(np.abs(actual - predicted)) / np.sum(np.abs(actual))

def seasonal_naive_forecast(df):
    """Predict units_sold using lag_7 (same day, one week ago) as the forecast."""
    df = df.copy()
    df['baseline_forecast'] = df['lag_7']
    return df

if __name__ == "__main__":
    df = pd.read_csv('data/processed/features.csv')
    df['date'] = pd.to_datetime(df['date'])

    # Use the last 8 weeks of data as a holdout test set (rolling-origin style)
    cutoff_date = df['date'].max() - pd.Timedelta(weeks=8)
    train = df[df['date'] <= cutoff_date]
    test = df[df['date'] > cutoff_date].copy()

    test = seasonal_naive_forecast(test)
    test = test.dropna(subset=['baseline_forecast'])

    baseline_wape = wape(test['units_sold'].values, test['baseline_forecast'].values)

    print(f"Train period: up to {cutoff_date.date()}")
    print(f"Test period: {test['date'].min().date()} to {test['date'].max().date()}")
    print(f"Test set size: {len(test)} rows")
    print(f"\nBASELINE (Seasonal-Naive) WAPE: {baseline_wape:.4f} ({baseline_wape*100:.2f}%)")
    print("\nThis is the number our ML model must beat.")