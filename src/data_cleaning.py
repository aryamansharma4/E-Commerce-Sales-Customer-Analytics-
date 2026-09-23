import pandas as pd
import sqlite3
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config.config import RAW_DATA_PATH, CLEANED_DATA_PATH, DB_PATH

def clean_ecommerce_data(input_path=RAW_DATA_PATH, output_path=CLEANED_DATA_PATH, db_path=DB_PATH):
    """
    Cleans raw e-commerce transaction data and writes cleaned CSV + populates SQLite DB.
    """
    print("--- Phase 1: Data Cleaning ---")
    if not Path(input_path).exists():
        raise FileNotFoundError(f"Raw data file not found at {input_path}. Please run generate_synthetic_data.py first.")

    df = pd.read_csv(input_path)
    initial_rows = len(df)
    print(f"Initial raw transactions count: {initial_rows}")

    # 1. Remove exact duplicate rows
    df = df.drop_duplicates()
    dups_removed = initial_rows - len(df)
    print(f"Removed {dups_removed} duplicate rows.")

    # 2. Remove missing CustomerID or TransactionID
    before_null = len(df)
    df = df.dropna(subset=['CustomerID', 'TransactionID'])
    print(f"Removed {before_null - len(df)} rows with missing CustomerID/TransactionID.")

    # 3. Clean invalid quantities and unit prices (returns/invalid records)
    before_invalid = len(df)
    df = df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0)]
    print(f"Removed {before_invalid - len(df)} rows with invalid Quantity or UnitPrice.")

    # 4. Standardize Data Types
    df['TransactionDate'] = pd.to_datetime(df['TransactionDate'])
    df['CustomerID'] = df['CustomerID'].astype(str)
    df['Quantity'] = df['Quantity'].astype(int)
    df['UnitPrice'] = df['UnitPrice'].round(2)

    # 5. Calculate Revenue
    df['Revenue'] = (df['Quantity'] * df['UnitPrice']).round(2)

    # Sort chronologically
    df = df.sort_values(by='TransactionDate').reset_index(drop=True)

    print(f"Cleaned dataset final transaction count: {len(df)}")

    # Export to Processed CSV
    df.to_csv(output_path, index=False)
    print(f"Cleaned dataset saved to: {output_path}")

    # Save to SQLite Database
    conn = sqlite3.connect(db_path)
    df.to_sql('transactions', conn, if_exists='replace', index=False)
    
    # Create indexes for fast querying
    cursor = conn.cursor()
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cust_id ON transactions (CustomerID);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tx_date ON transactions (TransactionDate);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cat ON transactions (ProductCategory);")
    conn.commit()
    conn.close()
    print(f"Transactions stored in SQLite DB at: {db_path} ('transactions' table)")

    return df

if __name__ == "__main__":
    clean_ecommerce_data()
