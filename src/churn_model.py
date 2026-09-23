import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, classification_report
import joblib
import sqlite3
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config.config import CUSTOMER_FEATURES_PATH, CHURN_PREDICTIONS_PATH, CHURN_ACTION_LIST_PATH, CHURN_MODEL_PATH, DB_PATH, CHURN_INACTIVITY_DAYS, RANDOM_STATE

def train_churn_model(input_path=CUSTOMER_FEATURES_PATH, output_path=CHURN_PREDICTIONS_PATH, db_path=DB_PATH):
    """
    Supervised ML module for Churn Prediction:
    - Defines Churn (no purchase in past 60 days)
    - Trains RandomForest Classifier
    - Computes churn probability & risk categories
    - Exports predictions & high-risk action list
    """
    print("--- Phase 4: Churn Prediction ML Model ---")
    if not Path(input_path).exists():
        raise FileNotFoundError(f"Customer features file not found at {input_path}.")

    df = pd.read_csv(input_path)

    # 1. Define Churn Label based on Recency threshold
    df['Churn'] = (df['Recency'] > CHURN_INACTIVITY_DAYS).astype(int)
    churn_rate = df['Churn'].mean() * 100
    print(f"Churn Label Definition: Inactivity > {CHURN_INACTIVITY_DAYS} days.")
    print(f"Total Customers: {len(df)} | Churned: {df['Churn'].sum()} ({churn_rate:.1f}%) | Active: {(df['Churn']==0).sum()}")

    # 2. Feature Selection
    feature_cols = [
        'Frequency', 'Monetary', 'AvgOrderValue', 'TotalProducts', 
        'UniqueCategories', 'CustomerTenureDays', 'AvgDaysBetweenOrders'
    ]
    # Note: Recency is intentionally excluded from training features to avoid target leakage (since target is defined by Recency threshold)

    X = df[feature_cols]
    y = df['Churn']

    # 3. Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=RANDOM_STATE, stratify=y
    )

    # 4. Model Training
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=6,
        random_state=RANDOM_STATE,
        class_weight='balanced'
    )
    model.fit(X_train, y_train)

    # 5. Model Evaluation
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    auc = roc_auc_score(y_test, y_prob)

    print("\nModel Evaluation Metrics (Test Set):")
    print(f"  - Accuracy:  {acc:.4f}")
    print(f"  - Precision: {prec:.4f}")
    print(f"  - Recall:    {rec:.4f}")
    print(f"  - F1-Score:  {f1:.4f}")
    print(f"  - ROC-AUC:   {auc:.4f}")

    # Feature Importance
    importances = pd.Series(model.feature_importances_, index=feature_cols).sort_values(ascending=False)
    print("\nFeature Importances:")
    for feat, imp in importances.items():
        print(f"  - {feat:22s}: {imp:.4f}")

    # Save trained model
    joblib.dump(model, CHURN_MODEL_PATH)
    print(f"\nTrained Churn Model saved to: {CHURN_MODEL_PATH}")

    # 6. Full Dataset Predictions
    df['ChurnProbability'] = model.predict_proba(X)[:, 1].round(4)

    # Define Risk Categories
    def assign_risk_category(prob):
        if prob >= 0.70:
            return 'High Risk'
        elif prob >= 0.40:
            return 'Medium Risk'
        else:
            return 'Low Risk'

    df['RiskCategory'] = df['ChurnProbability'].apply(assign_risk_category)

    print("\nChurn Risk Distribution across all customers:")
    risk_counts = df['RiskCategory'].value_counts()
    for risk, count in risk_counts.items():
        print(f"  - {risk:12s}: {count} customers ({count/len(df)*100:.1f}%)")

    # 7. Output Files
    output_cols = [
        'CustomerID', 'Recency', 'Frequency', 'Monetary', 'AvgOrderValue',
        'PrimaryCategory', 'Country', 'Churn', 'ChurnProbability', 'RiskCategory'
    ]
    df_out = df[output_cols]
    df_out.to_csv(output_path, index=False)
    print(f"Churn predictions saved to: {output_path}")

    # Export High Risk Customer Action List for Marketing/CRM
    high_risk_df = df_out[df_out['RiskCategory'] == 'High Risk'].sort_values(by='Monetary', ascending=False)
    high_risk_df.to_csv(CHURN_ACTION_LIST_PATH, index=False)
    print(f"High-Risk Customer Action List saved to: {CHURN_ACTION_LIST_PATH} ({len(high_risk_df)} customers)")

    # Save to SQLite DB
    conn = sqlite3.connect(db_path)
    df_out.to_sql('churn_predictions', conn, if_exists='replace', index=False)
    conn.commit()
    conn.close()
    print("Churn predictions saved to SQLite DB table 'churn_predictions'.")

    return df_out

if __name__ == "__main__":
    train_churn_model()
