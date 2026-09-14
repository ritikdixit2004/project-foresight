"""
Project FORESIGHT — ML Demand Forecasting Model
"""
import pandas as pd
import numpy as np
import lightgbm as lgb

def wape(actual, predicted):
    return np.sum(np.abs(actual - predicted)) / np.sum(np.abs(actual))

FEATURE_COLS = [
    'lag_1', 'lag_7', 'lag_14', 'lag_28',
    'rolling_mean_7', 'rolling_mean_14', 'rolling_mean_28',
    'day_of_week', 'is_weekend', 'month_num', 'is_holiday_flag', 'promo_flag'
]

if __name__ == "__main__":
    df = pd.read_csv('data/processed/features.csv')
    df['date'] = pd.to_datetime(df['date'])

    # Same split as baseline — last 8 weeks held out for testing
    cutoff_date = df['date'].max() - pd.Timedelta(weeks=8)
    train = df[df['date'] <= cutoff_date].copy()
    test = df[df['date'] > cutoff_date].copy()

    X_train, y_train = train[FEATURE_COLS], train['units_sold']
    X_test, y_test = test[FEATURE_COLS], test['units_sold']

    model = lgb.LGBMRegressor(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=6,
        random_state=42,
        verbosity=-1
    )
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    predictions = np.clip(predictions, 0, None)  # demand can't be negative

    model_wape = wape(y_test.values, predictions)

    # Compare against baseline (seasonal-naive, using lag_7)
    baseline_wape = wape(y_test.values, test['lag_7'].values)

    print(f"Test period: {test['date'].min().date()} to {test['date'].max().date()}")
    print(f"Test set size: {len(test)} rows\n")
    print(f"Baseline (Seasonal-Naive) WAPE: {baseline_wape:.4f} ({baseline_wape*100:.2f}%)")
    print(f"LightGBM Model WAPE:            {model_wape:.4f} ({model_wape*100:.2f}%)")

    improvement = (baseline_wape - model_wape) / baseline_wape * 100
    if model_wape < baseline_wape:
        print(f"\n✅ Model BEATS baseline by {improvement:.1f}%")
    else:
        print(f"\n⚠️ Model does NOT beat baseline. Ship the baseline and report this honestly.")

    # Feature importance — which signals matter most
    importance = pd.Series(model.feature_importances_, index=FEATURE_COLS).sort_values(ascending=False)
    print("\nFeature Importance:")
    print(importance)

    # Save predictions for later use in risk scoring / dashboard
    test_out = test[['date', 'sku_id', 'units_sold']].copy()
    test_out['forecast'] = predictions
    test_out.to_csv('data/processed/forecast_results.csv', index=False)
    print("\nSaved: data/processed/forecast_results.csv")