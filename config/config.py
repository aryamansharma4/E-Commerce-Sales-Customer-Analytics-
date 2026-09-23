import os
from pathlib import Path

# Base Directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Data Directories
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# File Paths
RAW_DATA_PATH = RAW_DATA_DIR / "ecommerce_transactions.csv"
CLEANED_DATA_PATH = PROCESSED_DATA_DIR / "cleaned_transactions.csv"
CUSTOMER_FEATURES_PATH = PROCESSED_DATA_DIR / "customer_features.csv"
CHURN_PREDICTIONS_PATH = PROCESSED_DATA_DIR / "churn_predictions.csv"
CUSTOMER_SEGMENTS_PATH = PROCESSED_DATA_DIR / "customer_segments.csv"
FORECASTS_PATH = PROCESSED_DATA_DIR / "forecasts.csv"

# Models Directory
MODELS_DIR = BASE_DIR / "models"
SCALER_PATH = MODELS_DIR / "scaler.pkl"
CLUSTERING_MODEL_PATH = MODELS_DIR / "clustering_model.pkl"
CHURN_MODEL_PATH = MODELS_DIR / "churn_model.pkl"

# Outputs Directory
OUTPUTS_DIR = BASE_DIR / "outputs"
REPORTS_DIR = OUTPUTS_DIR / "reports"
PREDICTIONS_DIR = OUTPUTS_DIR / "predictions"
EXECUTIVE_SUMMARY_JSON = REPORTS_DIR / "executive_summary.json"
EXECUTIVE_SUMMARY_MD = REPORTS_DIR / "executive_summary.md"
CHURN_ACTION_LIST_PATH = PREDICTIONS_DIR / "churn_risk_action_list.csv"

# Dashboard Directory
DASHBOARD_DIR = BASE_DIR / "dashboard"
POWERBI_DATA_DIR = DASHBOARD_DIR / "powerbi_data_sources"

# Database Config (SQLite default, expandable to MySQL/PostgreSQL)
DB_PATH = BASE_DIR / "data" / "ecommerce.db"
SQLITE_URL = f"sqlite:///{DB_PATH}"

# Pipeline & ML Hyperparameters
RANDOM_STATE = 42
CHURN_INACTIVITY_DAYS = 60
N_CLUSTERS = 4
FORECAST_PERIOD_DAYS = 30

# GenAI Config
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL_NAME = "gemini-1.5-flash"

# Ensure required directories exist
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR, REPORTS_DIR, PREDICTIONS_DIR, POWERBI_DATA_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
