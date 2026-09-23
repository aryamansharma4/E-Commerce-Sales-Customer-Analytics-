import pandas as pd
import json
import sqlite3
import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config.config import (
    DB_PATH, CLEANED_DATA_PATH, CUSTOMER_SEGMENTS_PATH, CHURN_PREDICTIONS_PATH, 
    FORECASTS_PATH, EXECUTIVE_SUMMARY_JSON, EXECUTIVE_SUMMARY_MD, 
    GEMINI_API_KEY, GEMINI_MODEL_NAME
)

def compile_kpi_payload(db_path=DB_PATH):
    """
    Extracts key performance indicators and ML model summaries from database tables into a clean JSON structure.
    """
    conn = sqlite3.connect(db_path)

    # 1. Financial & Volume Overview
    overview_query = """
    SELECT 
        SUM(Revenue) AS TotalRevenue,
        COUNT(DISTINCT TransactionID) AS TotalOrders,
        COUNT(DISTINCT CustomerID) AS TotalCustomers,
        AVG(Revenue) AS OverallAvgOrderValue
    FROM transactions;
    """
    overview_df = pd.read_sql_query(overview_query, conn)
    
    total_rev = float(overview_df['TotalRevenue'].iloc[0])
    total_orders = int(overview_df['TotalOrders'].iloc[0])
    total_cust = int(overview_df['TotalCustomers'].iloc[0])
    avg_order_val = float(overview_df['OverallAvgOrderValue'].iloc[0])

    # 2. Category Performance
    cat_query = """
    SELECT 
        ProductCategory, 
        SUM(Revenue) AS CategoryRevenue, 
        SUM(Quantity) AS UnitsSold
    FROM transactions 
    GROUP BY ProductCategory 
    ORDER BY CategoryRevenue DESC;
    """
    cat_df = pd.read_sql_query(cat_query, conn)
    top_cat = cat_df.iloc[0]['ProductCategory'] if not cat_df.empty else "N/A"
    top_cat_rev = float(cat_df.iloc[0]['CategoryRevenue']) if not cat_df.empty else 0.0

    # 3. Customer Segment Breakdown
    seg_query = """
    SELECT 
        CustomerSegment, 
        COUNT(CustomerID) AS CustomerCount,
        SUM(Monetary) AS SegmentRevenue,
        AVG(Recency) AS AvgRecency
    FROM customer_segments 
    GROUP BY CustomerSegment;
    """
    seg_df = pd.read_sql_query(seg_query, conn)
    segments_summary = seg_df.to_dict(orient='records')

    # 4. Churn Risk Summary
    churn_query = """
    SELECT 
        RiskCategory, 
        COUNT(CustomerID) AS CustomerCount,
        SUM(Monetary) AS RevenueAtRisk
    FROM churn_predictions 
    GROUP BY RiskCategory;
    """
    churn_df = pd.read_sql_query(churn_query, conn)
    churn_summary = churn_df.to_dict(orient='records')

    high_risk_cust = int(churn_df[churn_df['RiskCategory']=='High Risk']['CustomerCount'].sum()) if 'High Risk' in churn_df['RiskCategory'].values else 0
    high_risk_rev = float(churn_df[churn_df['RiskCategory']=='High Risk']['RevenueAtRisk'].sum()) if 'High Risk' in churn_df['RiskCategory'].values else 0.0

    # 5. Sales Forecast Metrics
    forecast_df = pd.read_sql_query("SELECT * FROM sales_forecasts", conn)
    conn.close()

    forecast_df['Date'] = pd.to_datetime(forecast_df['Date'])
    actual_rows = forecast_df[forecast_df['DataType'] == 'Historical'].sort_values('Date')
    forecast_rows = forecast_df[forecast_df['DataType'] == 'Forecast'].sort_values('Date')

    last_30_rev = float(actual_rows.tail(30)['ActualRevenue'].sum())
    next_30_forecast_rev = float(forecast_rows['PredictedRevenue'].sum())
    pct_change = float(((next_30_forecast_rev - last_30_rev) / last_30_rev) * 100) if last_30_rev > 0 else 0.0

    payload = {
        "financial_overview": {
            "total_revenue": round(total_rev, 2),
            "total_orders": total_orders,
            "total_customers": total_cust,
            "average_order_value": round(avg_order_val, 2)
        },
        "top_category": {
            "name": top_cat,
            "revenue": round(top_cat_rev, 2),
            "share_of_total_pct": round((top_cat_rev / total_rev) * 100, 1) if total_rev > 0 else 0
        },
        "customer_segmentation": segments_summary,
        "churn_risk_analysis": {
            "high_risk_customer_count": high_risk_cust,
            "high_risk_revenue_at_risk": round(high_risk_rev, 2),
            "breakdown": churn_summary
        },
        "sales_forecasting": {
            "last_30_day_actual_revenue": round(last_30_rev, 2),
            "next_30_day_predicted_revenue": round(next_30_forecast_rev, 2),
            "projected_revenue_change_pct": round(pct_change, 2)
        }
    }

    # Save to JSON file
    with open(EXECUTIVE_SUMMARY_JSON, 'w') as f:
        json.dump(payload, f, indent=2)
    
    print(f"Aggregated KPI Payload compiled and saved to: {EXECUTIVE_SUMMARY_JSON}")
    return payload

def generate_ai_executive_insights(payload=None):
    """
    Feeds KPI payload to Gemini API (or robust analytical template generator if no API key)
    to produce executive insights and management recommendations.
    """
    print("--- Phase 6: GenAI Executive Insights & Strategy Generator ---")
    if payload is None:
        payload = compile_kpi_payload()

    api_key = GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", "")

    if api_key:
        print("Connecting to Google Gemini API...")
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(GEMINI_MODEL_NAME)

            prompt = f"""
You are an expert Chief Commercial Officer & Data Science Strategist.
Analyze the following e-commerce executive business metrics and ML predictions JSON payload:

{json.dumps(payload, indent=2)}

Generate a formal executive summary and strategic management recommendations report.
Structure your response in Markdown with the following headers:
# Executive Summary & Commercial Strategy Report

## 1. Executive Performance Overview
- Bullet points summarizing financial revenue, order volumes, and top category performance.

## 2. Customer Segmentation & Value Analysis
- Key findings from the K-Means RFM segmentation results.

## 3. Churn Risk & Revenue Exposure
- Analysis of high-risk customers, churn probability trends, and revenue at risk.

## 4. 30-Day Revenue & Demand Forecast
- Insights on the projected 30-day sales trajectory.

## 5. Strategic Action Plan & Executive Recommendations
- 4 prioritized, actionable, high-impact business recommendations for C-suite management.
"""
            response = model.generate_content(prompt)
            markdown_content = response.text
            print("Successfully generated Executive Report via Gemini API!")

        except Exception as e:
            print(f"Gemini API call encountered an error: {e}. Falling back to analytical template engine.")
            markdown_content = generate_analytical_template_report(payload)
    else:
        print("No GEMINI_API_KEY detected in environment or config. Using analytical template engine...")
        markdown_content = generate_analytical_template_report(payload)

    # Write report to markdown file
    with open(EXECUTIVE_SUMMARY_MD, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

    print(f"Executive Report saved to: {EXECUTIVE_SUMMARY_MD}")
    return markdown_content

def generate_analytical_template_report(p):
    """
    Generates a deterministic analytical Markdown Executive Report from structured KPIs.
    """
    fin = p['financial_overview']
    cat = p['top_category']
    churn = p['churn_risk_analysis']
    fc = p['sales_forecasting']
    
    trend_direction = "an increase" if fc['projected_revenue_change_pct'] >= 0 else "a decline"
    trend_adjective = "positive" if fc['projected_revenue_change_pct'] >= 0 else "concerning"

    report = f"""# Executive Summary & Commercial Strategy Report

> **Automated AI Business Intelligence System**  
> *Generated based on SQL KPIs, K-Means Clustering, RandomForest Churn ML, and Time-Series Sales Forecasts.*

---

## 1. Executive Performance Overview

* **Total Revenue:** ${fin['total_revenue']:,.2f} generated across {fin['total_orders']:,} completed transactions.
* **Customer Base:** {fin['total_customers']:,} unique active customers with an **Average Order Value (AOV)** of ${fin['average_order_value']:.2f}.
* **Category Leader:** **{cat['name']}** is the highest revenue-generating category, accounting for **${cat['revenue']:,.2f}** ({cat['share_of_total_pct']}% of total gross revenue).

---

## 2. Customer Segmentation & Value Analysis (K-Means RFM)

The customer base has been categorized into distinct behavioral clusters using standardized Recency, Frequency, and Monetary metrics:

"""
    for seg in p['customer_segmentation']:
        report += f"* **{seg['CustomerSegment']}:** {seg['CustomerCount']:,} customers | Total Revenue: ${seg['SegmentRevenue']:,.2f} | Avg Recency: {seg['AvgRecency']:.1f} days\n"

    report += f"""
---

## 3. Churn Risk & Revenue Exposure (RandomForest Classifier)

Our supervised machine learning model identified significant churn risk exposure requiring immediate intervention:

* **High-Risk Customers:** **{churn['high_risk_customer_count']:,} customers** exhibit a >70% probability of stopping future purchases.
* **Revenue at Risk:** **${churn['high_risk_revenue_at_risk']:,.2f}** in gross lifetime value is at imminent risk of churn.
* **Risk Breakdown:**
"""
    for ch in churn['breakdown']:
        report += f"  - **{ch['RiskCategory']}:** {ch['CustomerCount']:,} customers (${ch['RevenueAtRisk']:,.2f} total spend)\n"

    report += f"""
---

## 4. 30-Day Revenue & Demand Forecast (Time-Series Analytics)

* **Previous 30-Day Actual Revenue:** ${fc['last_30_day_actual_revenue']:,.2f}
* **Next 30-Day Projected Revenue:** ${fc['next_30_day_predicted_revenue']:,.2f}
* **Forecasted Growth Trajectory:** Projected **{trend_direction} of {abs(fc['projected_revenue_change_pct']):.1f}%** over the next 30 days. This indicates {trend_adjective} momentum for inventory and cash flow planning.

---

## 5. Strategic Action Plan & Executive Recommendations

1. **Immediate High-Risk VIP Retention Campaign:** Launch targeted win-back promotions for the {churn['high_risk_customer_count']} high-risk customers, protecting up to ${churn['high_risk_revenue_at_risk']:,.2f} in revenue.
2. **Category Inventory Optimization:** Increase stock allocations for **{cat['name']}** to prevent stockouts during projected demand surges.
3. **VIP Loyalty Tier Expansion:** Implement exclusive perks for High-Value VIP segments to increase order frequency and boost baseline AOV beyond ${fin['average_order_value']:.2f}.
4. **Automated Triggered Marketing:** Deploy automated email triggers for customers entering the 45-60 day inactivity window before they transition to high-risk churn status.
"""
    return report

if __name__ == "__main__":
    generate_ai_executive_insights()
