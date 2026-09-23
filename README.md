# E-Commerce Customer Intelligence & Sales Analytics System

An end-to-end Data Science, Machine Learning, Generative AI, and Business Intelligence platform built to optimize e-commerce operations, customer retention, sales forecasting, and commercial decision-making.

---

## 📌 Executive Summary & Business Impact

This system transforms raw transactional e-commerce data into actionable executive intelligence by answering four foundational business questions:

1. **Who are our customers?**  
   → **RFM + K-Means Clustering** categorizes customers into distinct behavioral segments (*High-Value VIPs*, *Loyal Regulars*, *Occasional Buyers*, *At-Risk / Inactive*).
2. **Which customers are likely to stop buying?**  
   → **Supervised Churn ML (Random Forest Classifier)** predicts 60-day customer churn probabilities and flags high-risk accounts.
3. **What are we likely to sell next?**  
   → **Time-Series Forecasting (Prophet / Holt-Winters)** projects 30-day daily sales volume and revenue with 95% confidence intervals.
4. **What should management do about the results?**  
   → **GenAI Layer (Google Gemini API / Rule Engine)** generates executive reports, C-suite recommendations, and automated segment-targeted marketing campaigns.

---

## 🏗️ System Architecture & Workflow

```
                RAW E-COMMERCE TRANSACTIONS (~50,000 Rows)
                                    │
                                    ▼
                          DATA CLEANING & SQL DB
                       (src/data_cleaning.py & SQL)
                                    │
                                    ▼
                           FEATURE ENGINEERING
                      (src/feature_engineering.py)
                ┌───────────────────┼───────────────────┐
                ▼                   ▼                   ▼
              RFM               Churn             Time Series
            Features           Features            Features
                │                   │                   │
                ▼                   ▼                   ▼
             K-Means             Random              Prophet /
            Clustering           Forest             Time-Series
        (segmentation.py)   (churn_model.py)      (forecasting.py)
                │                   │                   │
                └───────────────────┼───────────────────┘
                                    ▼
                              ML RESULTS CSVs
                                    │
                                    ▼
                              GENAI LAYER
                    (genai_insights.py & campaign.py)
                        ┌───────────┴───────────┐
                        ▼                       ▼
                  Executive Summary      Campaign Generator
                        │                       │
                        └───────────┬───────────┘
                                    ▼
                           POWER BI DASHBOARD
```

---

## 📁 Repository Structure

```
E-Commerce Customer Intelligence & Sales Analytics/
│
├── config/
│   └── config.py                     # Central configuration, file paths, DB & API settings
│
├── data/
│   ├── raw/
│   │   └── ecommerce_transactions.csv# Raw transactions CSV (~50,000 records)
│   ├── processed/
│   │   ├── cleaned_transactions.csv  # Cleaned, deduplicated dataset with calculated revenue
│   │   ├── customer_features.csv     # RFM metrics & customer aggregations
│   │   ├── churn_predictions.csv     # Churn probabilities & risk categories
│   │   ├── customer_segments.csv     # K-Means clusters & segment business labels
│   │   └── forecasts.csv             # 30-day revenue forecast with confidence bounds
│   └── ecommerce.db                  # Embedded SQLite Database mirroring all tables
│
├── models/
│   ├── scaler.pkl                    # Trained StandardScaler for RFM features
│   ├── clustering_model.pkl          # Trained KMeans clustering model
│   └── churn_model.pkl               # Trained RandomForest churn classifier
│
├── sql/
│   ├── schema.sql                    # Database table schemas
│   ├── data_cleaning.sql             # SQL data sanitation & quality checks
│   ├── customer_analysis.sql         # SQL RFM, segment summary, & churn queries
│   └── sales_analysis.sql            # SQL monthly, category, and daily sales queries
│
├── src/
│   ├── generate_synthetic_data.py    # Realistic synthetic transaction dataset generator
│   ├── data_cleaning.py              # Data cleaning, null handling, revenue calculation
│   ├── feature_engineering.py        # RFM metrics & behavioral aggregation features
│   ├── segmentation.py               # K-Means clustering & cluster profiling
│   ├── churn_model.py                # Supervised Churn ML training & risk scoring
│   ├── forecasting.py                # Time-series revenue forecasting
│   ├── genai_insights.py             # KPI aggregation & GenAI Executive Summary report
│   └── campaign_generator.py         # Automated segment marketing campaign copy generator
│
├── notebooks/
│   ├── 01_data_exploration.ipynb     # EDA, data sanitation, & visual distributions
│   ├── 02_customer_segmentation.ipynb # Elbow method, Silhouette analysis, & cluster profiles
│   ├── 03_churn_prediction.ipynb     # Model evaluation, ROC-AUC, & feature importances
│   └── 04_demand_forecasting.ipynb   # Time-series decomposition & 30-day forecast plot
│
├── outputs/
│   ├── reports/
│   │   ├── executive_summary.json    # Aggregated KPI payload
│   │   ├── executive_summary.md      # AI Executive Report & Strategic Recommendations
│   │   └── campaign_at_risk_inactive.md # Generated targeted campaign copy
│   └── predictions/
│       └── churn_risk_action_list.csv# High-risk customer action list for CRM/marketing
│
├── dashboard/
│   ├── powerbi_setup_guide.md        # Page-by-page visual blueprint for Power BI Desktop
│   └── powerbi_data_sources/         # Exported CSV data sources optimized for Power BI
│
├── main.py                           # End-to-end master pipeline orchestrator
├── requirements.txt                  # Python dependencies
└── README.md                         # Project documentation
```

---

## ⚡ Quick Start Guide & Instructions

### Step 1: Clone & Navigate to Project Directory
```bash
cd "C:\Users\chait\OneDrive\Desktop\My projects\E-Commerce Customer Intelligence & Sales Analytics"
```

### Step 2: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Optional GenAI API Key (Google Gemini)
To enable real-time LLM executive summary generation via Gemini API:
Set the environment variable or edit `config/config.py`:
```bash
# Windows PowerShell
$env:GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
```
*(Note: If no API key is provided, the system seamlessly uses an offline analytical rule-based engine).*

### Step 4: Run the End-to-End Pipeline
Execute the master orchestrator:
```bash
python main.py
```

This single command will:
1. Generate ~50,000 realistic synthetic transaction records.
2. Clean data and load into SQLite database `data/ecommerce.db`.
3. Compute RFM customer features.
4. Train and evaluate K-Means Customer Segmentation.
5. Train and evaluate RandomForest Churn ML model.
6. Generate 30-day sales forecast.
7. Generate GenAI Executive Report (`outputs/reports/executive_summary.md`).
8. Generate segment-targeted marketing campaigns.
9. Sync Power BI data files into `dashboard/powerbi_data_sources/`.

---

## 📊 Building the Power BI Dashboard

1. Open **Power BI Desktop**.
2. Open `dashboard/powerbi_setup_guide.md` for page-by-page layout instructions.
3. Import CSVs from `dashboard/powerbi_data_sources/` (or connect directly to `data/ecommerce.db`).
4. Build the 4 pages:
   - **Page 1:** Executive Overview (Revenue, Orders, Category breakdown, Country map)
   - **Page 2:** Customer Intelligence (RFM scatter, Segment share, Segment revenue)
   - **Page 3:** Predictive Analytics (Churn probability distribution, 30-day forecast line chart with confidence bounds)
   - **Page 4:** AI Business Insights & Campaign Generator (Executive Markdown summary card & segment campaign selector)

---

## 🛠️ Tech Stack

- **Language & Data Processing:** Python 3.11+, Pandas, NumPy
- **Database & SQL:** SQLite (Embedded DB), SQL Queries (`.sql`)
- **Machine Learning:** Scikit-Learn (K-Means, RandomForest), XGBoost
- **Time-Series Forecasting:** Prophet / Statsmodels (Holt-Winters Exponential Smoothing)
- **Generative AI:** Google Gemini API (`google-generativeai`)
- **Business Intelligence:** Power BI Desktop
- **Visualization:** Matplotlib, Seaborn
