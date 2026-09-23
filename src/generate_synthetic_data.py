import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config.config import RAW_DATA_PATH, RANDOM_STATE

def generate_ecommerce_data(num_transactions=50000, num_customers=1500, start_date="2024-01-01", end_date="2025-06-30"):
    """
    Generates realistic synthetic e-commerce transaction dataset with intentional noise for data cleaning demonstration.
    """
    np.random.seed(RANDOM_STATE)
    random.seed(RANDOM_STATE)

    categories = {
        'Electronics': {'price_range': (50, 1500), 'qty_range': (1, 3), 'weight': 0.20},
        'Apparel': {'price_range': (15, 150), 'qty_range': (1, 5), 'weight': 0.25},
        'Home & Kitchen': {'price_range': (20, 400), 'qty_range': (1, 4), 'weight': 0.20},
        'Beauty & Personal Care': {'price_range': (10, 100), 'qty_range': (1, 6), 'weight': 0.15},
        'Sports & Outdoors': {'price_range': (25, 300), 'qty_range': (1, 3), 'weight': 0.10},
        'Books': {'price_range': (8, 60), 'qty_range': (1, 4), 'weight': 0.10},
    }

    products_by_category = {
        'Electronics': [f'P_ELEC_{i:03d}' for i in range(1, 31)],
        'Apparel': [f'P_APP_{i:03d}' for i in range(1, 41)],
        'Home & Kitchen': [f'P_HOME_{i:03d}' for i in range(1, 25)],
        'Beauty & Personal Care': [f'P_BEAU_{i:03d}' for i in range(1, 20)],
        'Sports & Outdoors': [f'P_SPRT_{i:03d}' for i in range(1, 20)],
        'Books': [f'P_BOOK_{i:03d}' for i in range(1, 25)],
    }

    countries = ['United States', 'United Kingdom', 'Germany', 'Canada', 'India', 'Australia']
    country_weights = [0.40, 0.20, 0.15, 0.10, 0.10, 0.05]

    payment_methods = ['Credit Card', 'PayPal', 'Debit Card', 'UPI', 'Net Banking']
    payment_weights = [0.45, 0.25, 0.15, 0.10, 0.05]

    # Generate customer profiles
    customer_ids = [f'CUST_{i:04d}' for i in range(1001, 1001 + num_customers)]
    customer_country = {c: np.random.choice(countries, p=country_weights) for c in customer_ids}
    
    # Assign customer activity profiles (VIP, Regular, At-Risk, One-Time)
    customer_types = np.random.choice(
        ['VIP', 'Regular', 'Casual', 'Churned_Early'],
        size=num_customers,
        p=[0.10, 0.45, 0.30, 0.15]
    )
    customer_type_map = dict(zip(customer_ids, customer_types))

    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    total_days = (end_dt - start_dt).days

    records = []
    category_list = list(categories.keys())
    cat_weights = [categories[c]['weight'] for c in category_list]

    for tx_id in range(1, num_transactions + 1):
        cust_id = random.choice(customer_ids)
        c_type = customer_type_map[cust_id]

        # Determine transaction date based on customer type
        if c_type == 'Churned_Early':
            # Stop buying after first 6 months
            day_offset = random.randint(0, min(180, total_days))
        elif c_type == 'VIP':
            # High frequency across all days
            day_offset = random.randint(0, total_days)
        else:
            day_offset = random.randint(0, total_days)

        tx_date = start_dt + timedelta(days=day_offset, hours=random.randint(8, 22), minutes=random.randint(0, 59))
        
        # Category & product selection
        cat = np.random.choice(category_list, p=cat_weights)
        prod = random.choice(products_by_category[cat])

        # Price and Quantity
        min_p, max_p = categories[cat]['price_range']
        unit_price = round(random.uniform(min_p, max_p), 2)
        min_q, max_q = categories[cat]['qty_range']
        
        if c_type == 'VIP':
            quantity = random.randint(min_q, max_q + 2)
            unit_price = round(unit_price * random.uniform(1.0, 1.3), 2)
        else:
            quantity = random.randint(min_q, max_q)

        country = customer_country[cust_id]
        payment = np.random.choice(payment_methods, p=payment_weights)

        records.append({
            'TransactionID': f'TXN_{tx_id:06d}',
            'CustomerID': cust_id,
            'ProductID': prod,
            'ProductCategory': cat,
            'Quantity': quantity,
            'UnitPrice': unit_price,
            'TransactionDate': tx_date.strftime("%Y-%m-%d %H:%M:%S"),
            'Country': country,
            'PaymentMethod': payment
        })

    df = pd.DataFrame(records)

    # Introduce realistic dirty data for data_cleaning.py to fix:
    print("Injecting realistic dirty data for data cleaning script testing...")
    
    # 1. Duplicate rows (~0.5%)
    duplicates = df.sample(frac=0.005, random_state=RANDOM_STATE)
    df = pd.concat([df, duplicates], ignore_index=True)

    # 2. Missing CustomerID (~0.3%)
    df.loc[df.sample(frac=0.003, random_state=RANDOM_STATE).index, 'CustomerID'] = np.nan

    # 3. Invalid negative quantities/prices (~0.4%)
    bad_qty_idx = df.sample(frac=0.002, random_state=RANDOM_STATE).index
    df.loc[bad_qty_idx, 'Quantity'] = df.loc[bad_qty_idx, 'Quantity'] * -1

    bad_price_idx = df.sample(frac=0.002, random_state=RANDOM_STATE + 1).index
    df.loc[bad_price_idx, 'UnitPrice'] = df.loc[bad_price_idx, 'UnitPrice'] * -1

    # Save to RAW_DATA_PATH
    df.to_csv(RAW_DATA_PATH, index=False)
    print(f"Successfully generated {len(df)} transactions and saved to {RAW_DATA_PATH}")
    return df

if __name__ == "__main__":
    generate_ecommerce_data()
