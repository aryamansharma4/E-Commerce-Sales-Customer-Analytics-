import sys
import shutil
from pathlib import Path

# Add project root directory to path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

from config.config import (
    RAW_DATA_PATH, PROCESSED_DATA_DIR, POWERBI_DATA_DIR, REPORTS_DIR
)
from src.generate_synthetic_data import generate_ecommerce_data
from src.data_cleaning import clean_ecommerce_data
from src.feature_engineering import build_customer_features
from src.segmentation import run_customer_segmentation
from src.churn_model import train_churn_model
from src.forecasting import generate_sales_forecast
from src.genai_insights import compile_kpi_payload, generate_ai_executive_insights
from src.campaign_generator import generate_campaign_for_segment

def run_end_to_end_pipeline():
    """
    Orchestrates the full end-to-end E-Commerce Customer Intelligence & Sales Analytics pipeline.
    """
    print("=" * 80)
    print(" E-COMMERCE CUSTOMER INTELLIGENCE & SALES ANALYTICS SYSTEM")
    print(" End-to-End Automated Pipeline Execution")
    print("=" * 80 + "\n")

    # Step 1: Data Generation (if raw CSV missing)
    if not RAW_DATA_PATH.exists():
        print("Raw transaction data not found. Generating realistic synthetic dataset (~50,000 transactions)...")
        generate_ecommerce_data()
    else:
        print(f"Found existing raw transactions at {RAW_DATA_PATH}")

    # Step 2: Data Cleaning & SQL Ingestion
    clean_df = clean_ecommerce_data()

    # Step 3: Feature Engineering (RFM & Aggregations)
    feat_df = build_customer_features()

    # Step 4: Customer Segmentation (K-Means Clustering)
    seg_df = run_customer_segmentation()

    # Step 5: Churn Prediction ML Model
    churn_df = train_churn_model()

    # Step 6: Demand & Revenue Forecasting
    forecast_df = generate_sales_forecast()

    # Step 7: GenAI Executive Insights & KPI Aggregation
    kpi_payload = compile_kpi_payload()
    report_md = generate_ai_executive_insights(kpi_payload)

    # Step 8: GenAI Segment Campaign Generator
    print("\nGenerating segment-targeted marketing campaigns...")
    generate_campaign_for_segment("High-Value VIPs", "Electronics", 850.00, "Low Risk")
    generate_campaign_for_segment("At-Risk / Inactive", "Electronics", 320.00, "High Risk")

    # Step 9: Export Data Sources for Power BI Sync
    print("\nSynchronizing processed CSV files to Power BI data folder...")
    for csv_file in PROCESSED_DATA_DIR.glob("*.csv"):
        shutil.copy(csv_file, POWERBI_DATA_DIR / csv_file.name)
    print(f"Copied processed CSV files to: {POWERBI_DATA_DIR}")

    print("\n" + "=" * 80)
    print(" PIPELINE EXECUTION COMPLETED SUCCESSFULLY!")
    print(" All ML models, forecasts, SQL tables, and GenAI reports are ready.")
    print(" Next Step: Open Power BI Desktop and follow 'dashboard/powerbi_setup_guide.md'")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    run_end_to_end_pipeline()
