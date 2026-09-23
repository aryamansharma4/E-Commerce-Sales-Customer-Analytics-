import pandas as pd
import numpy as np
import sqlite3
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config.config import CLEANED_DATA_PATH, CUSTOMER_FEATURES_PATH, DB_PATH

def build_customer_features(input_path=CLEANED_DATA_PATH, output_path=CUSTOMER_FEATURES_PATH, db_path=DB_PATH):
    """
    Computes RFM (Recency, Frequency, Monetary) metrics and behavioral features for every customer.
    """
    print("--- Phase 2: Feature Engineering (RFM & Customer Aggregations) ---")
    if not Path(input_path).exists():
        raise FileNotFoundError(f"Cleaned data file not found at {input_path}.")

    df = pd.read_csv(input_path)
    df['TransactionDate'] = pd.to_datetime(df['TransactionDate'])

    # Snapshot Date = max transaction date + 1 day
    snapshot_date = df['TransactionDate'].max() + pd.Timedelta(days=1)
    print(f"Dataset snapshot date for RFM calculation: {snapshot_date.strftime('%Y-%m-%d')}")

    # Aggregations per customer
    features = df.groupby('CustomerID').agg(
        LastPurchaseDate=('TransactionDate', 'max'),
        FirstPurchaseDate=('TransactionDate', 'min'),
        Frequency=('TransactionID', 'nunique'),
        Monetary=('Revenue', 'sum'),
        TotalProducts=('Quantity', 'sum'),
        UniqueCategories=('ProductCategory', 'nunique'),
        PrimaryCategory=('ProductCategory', lambda x: x.mode()[0] if not x.empty else 'Unknown'),
        PreferredPaymentMethod=('PaymentMethod', lambda x: x.mode()[0] if not x.empty else 'Unknown'),
        Country=('Country', lambda x: x.mode()[0] if not x.empty else 'Unknown')
    ).reset_index()

    # Calculate Recency in Days
    features['Recency'] = (snapshot_date - features['LastPurchaseDate']).dt.days

    # Calculate Average Order Value (AOV)
    features['AvgOrderValue'] = (features['Monetary'] / features['Frequency']).round(2)

    # Customer Tenure in Days
    features['CustomerTenureDays'] = (snapshot_date - features['FirstPurchaseDate']).dt.days

    # Average Days Between Orders
    features['AvgDaysBetweenOrders'] = np.where(
        features['Frequency'] > 1,
        (features['CustomerTenureDays'] - features['Recency']) / (features['Frequency'] - 1),
        features['CustomerTenureDays']
    ).round(1)

    # Round monetary metric
    features['Monetary'] = features['Monetary'].round(2)

    # Convert timestamps to string for clean CSV & DB storage
    features['LastPurchaseDate'] = features['LastPurchaseDate'].dt.strftime('%Y-%m-%d %H:%M:%S')
    features['FirstPurchaseDate'] = features['FirstPurchaseDate'].dt.strftime('%Y-%m-%d %H:%M:%S')

    print(f"Generated feature vectors for {len(features)} unique customers.")

    # Save to Processed CSV
    features.to_csv(output_path, index=False)
    print(f"Customer features saved to: {output_path}")

    # Save to SQLite DB
    conn = sqlite3.connect(db_path)
    features.to_sql('customer_features', conn, if_exists='replace', index=False)
    conn.commit()
    conn.close()
    print(f"Customer features saved to SQLite DB table 'customer_features'.")

    return features

if __name__ == "__main__":
    build_customer_features()
