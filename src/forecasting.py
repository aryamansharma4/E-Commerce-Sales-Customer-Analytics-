import pandas as pd
import numpy as np
from datetime import timedelta
import sqlite3
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config.config import CLEANED_DATA_PATH, FORECASTS_PATH, DB_PATH, FORECAST_PERIOD_DAYS

def generate_sales_forecast(input_path=CLEANED_DATA_PATH, output_path=FORECASTS_PATH, db_path=DB_PATH, forecast_days=FORECAST_PERIOD_DAYS):
    """
    Time-Series Revenue & Order Forecasting:
    Aggregates daily sales and projects revenue 30 days into the future with lower/upper confidence bounds.
    Supports Prophet -> Statsmodels -> Scikit-learn Linear/Seasonal Regression fallback chain.
    """
    print("--- Phase 5: Demand & Revenue Forecasting ---")
    if not Path(input_path).exists():
        raise FileNotFoundError(f"Cleaned data file not found at {input_path}.")

    df = pd.read_csv(input_path)
    df['TransactionDate'] = pd.to_datetime(df['TransactionDate'])
    df['Date'] = df['TransactionDate'].dt.floor('D')

    # Aggregate Daily Sales
    daily_sales = df.groupby('Date').agg(
        ActualRevenue=('Revenue', 'sum'),
        OrderVolume=('TransactionID', 'nunique'),
        UnitsSold=('Quantity', 'sum')
    ).reset_index().sort_values('Date')

    # Ensure full date range with no missing dates
    full_date_range = pd.date_range(start=daily_sales['Date'].min(), end=daily_sales['Date'].max(), freq='D')
    daily_sales = daily_sales.set_index('Date').reindex(full_date_range).fillna(0).rename_axis('Date').reset_index()

    print(f"Historical daily sales date range: {daily_sales['Date'].min().strftime('%Y-%m-%d')} to {daily_sales['Date'].max().strftime('%Y-%m-%d')} ({len(daily_sales)} days)")

    # Fallback chain: Prophet -> statsmodels -> scikit-learn Linear/Seasonal model
    model_used = None
    
    try:
        from prophet import Prophet
        model_used = "Prophet"
    except ImportError:
        try:
            from statsmodels.tsa.holtwinters import ExponentialSmoothing
            model_used = "Statsmodels"
        except ImportError:
            model_used = "Scikit-Learn"

    print(f"Using forecasting engine: {model_used}")

    if model_used == "Prophet":
        from prophet import Prophet
        prophet_df = daily_sales[['Date', 'ActualRevenue']].rename(columns={'Date': 'ds', 'ActualRevenue': 'y'})
        model = Prophet(yearly_seasonality=True, weekly_seasonality=True, daily_seasonality=False, interval_width=0.95)
        model.fit(prophet_df)

        future = model.make_future_dataframe(periods=forecast_days)
        forecast = model.predict(future)

        results = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].rename(columns={
            'ds': 'Date',
            'yhat': 'PredictedRevenue',
            'yhat_lower': 'LowerBound',
            'yhat_upper': 'UpperBound'
        })
        
        merged = pd.merge(daily_sales, results, on='Date', how='outer')
        merged['LowerBound'] = merged['LowerBound'].clip(lower=0).round(2)
        merged['UpperBound'] = merged['UpperBound'].round(2)
        merged['PredictedRevenue'] = merged['PredictedRevenue'].clip(lower=0).round(2)
        merged['ActualRevenue'] = merged['ActualRevenue'].round(2)

    elif model_used == "Statsmodels":
        from statsmodels.tsa.holtwinters import ExponentialSmoothing
        ts_data = daily_sales.set_index('Date')['ActualRevenue']
        model = ExponentialSmoothing(ts_data, trend='add', seasonal='add', seasonal_periods=7).fit()

        last_date = daily_sales['Date'].max()
        future_dates = [last_date + timedelta(days=i) for i in range(1, forecast_days + 1)]
        
        pred = model.forecast(forecast_days)
        residual_std = np.std(model.resid)
        lower_bound = np.clip(pred - (1.96 * residual_std), a_min=0, a_max=None)
        upper_bound = pred + (1.96 * residual_std)

        future_df = pd.DataFrame({
            'Date': future_dates,
            'ActualRevenue': np.nan,
            'OrderVolume': np.nan,
            'UnitsSold': np.nan,
            'PredictedRevenue': pred.values.round(2),
            'LowerBound': lower_bound.values.round(2),
            'UpperBound': upper_bound.values.round(2)
        })

        hist_df = daily_sales.copy()
        hist_df['PredictedRevenue'] = hist_df['ActualRevenue']
        hist_df['LowerBound'] = hist_df['ActualRevenue']
        hist_df['UpperBound'] = hist_df['ActualRevenue']

        merged = pd.concat([hist_df, future_df], ignore_index=True)

    else: # Scikit-learn fallback (Linear Trend + Day-of-Week Seasonality)
        from sklearn.linear_model import Ridge
        
        ds_df = daily_sales.copy()
        ds_df['DayIndex'] = (ds_df['Date'] - ds_df['Date'].min()).dt.days
        ds_df['DayOfWeek'] = ds_df['Date'].dt.dayofweek

        # One-hot encode DayOfWeek for 7-day seasonality
        X_hist = pd.get_dummies(ds_df[['DayIndex', 'DayOfWeek']], columns=['DayOfWeek'], drop_first=True)
        y_hist = ds_df['ActualRevenue']

        model = Ridge(alpha=1.0)
        model.fit(X_hist, y_hist)

        # Generate future features
        last_date = daily_sales['Date'].max()
        future_dates = [last_date + timedelta(days=i) for i in range(1, forecast_days + 1)]
        future_df = pd.DataFrame({'Date': future_dates})
        future_df['DayIndex'] = (future_df['Date'] - ds_df['Date'].min()).dt.days
        future_df['DayOfWeek'] = future_df['Date'].dt.dayofweek
        
        X_future = pd.get_dummies(future_df[['DayIndex', 'DayOfWeek']], columns=['DayOfWeek'], drop_first=True)
        # Align columns
        X_future = X_future.reindex(columns=X_hist.columns, fill_value=0)

        pred = model.predict(X_future)
        residuals = y_hist - model.predict(X_hist)
        residual_std = np.std(residuals)

        lower_bound = np.clip(pred - (1.96 * residual_std), a_min=0, a_max=None)
        upper_bound = pred + (1.96 * residual_std)

        future_res_df = pd.DataFrame({
            'Date': future_dates,
            'ActualRevenue': np.nan,
            'OrderVolume': np.nan,
            'UnitsSold': np.nan,
            'PredictedRevenue': pred.round(2),
            'LowerBound': lower_bound.round(2),
            'UpperBound': upper_bound.round(2)
        })

        hist_df = daily_sales.copy()
        hist_df['PredictedRevenue'] = hist_df['ActualRevenue']
        hist_df['LowerBound'] = hist_df['ActualRevenue']
        hist_df['UpperBound'] = hist_df['ActualRevenue']

        merged = pd.concat([hist_df, future_res_df], ignore_index=True)

    # Classify Type ('Historical' vs 'Forecast')
    max_hist_date = daily_sales['Date'].max()
    merged['DataType'] = np.where(merged['Date'] <= max_hist_date, 'Historical', 'Forecast')
    merged['Date'] = merged['Date'].dt.strftime('%Y-%m-%d')

    # Summary Stats
    hist_revenue = daily_sales['ActualRevenue'].sum()
    last_30_revenue = daily_sales.tail(30)['ActualRevenue'].sum()
    forecast_30_revenue = merged[merged['DataType'] == 'Forecast']['PredictedRevenue'].sum()
    revenue_diff_pct = ((forecast_30_revenue - last_30_revenue) / last_30_revenue) * 100 if last_30_revenue > 0 else 0.0

    print(f"\n30-Day Revenue Forecasting Results:")
    print(f"  - Last 30-Day Actual Revenue:     ${last_30_revenue:,.2f}")
    print(f"  - Next 30-Day Predicted Revenue:  ${forecast_30_revenue:,.2f}")
    print(f"  - Projected Revenue Change:       {revenue_diff_pct:+.2f}%")

    # Save to Processed CSV
    merged.to_csv(output_path, index=False)
    print(f"\nForecast data saved to: {output_path}")

    # Save to SQLite DB
    conn = sqlite3.connect(db_path)
    merged.to_sql('sales_forecasts', conn, if_exists='replace', index=False)
    conn.commit()
    conn.close()
    print("Forecast data saved to SQLite DB table 'sales_forecasts'.")

    return merged

if __name__ == "__main__":
    generate_sales_forecast()
