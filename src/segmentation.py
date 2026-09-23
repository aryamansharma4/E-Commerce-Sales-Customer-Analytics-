import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import joblib
import sqlite3
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config.config import CUSTOMER_FEATURES_PATH, CUSTOMER_SEGMENTS_PATH, SCALER_PATH, CLUSTERING_MODEL_PATH, DB_PATH, N_CLUSTERS, RANDOM_STATE

def run_customer_segmentation(input_path=CUSTOMER_FEATURES_PATH, output_path=CUSTOMER_SEGMENTS_PATH, db_path=DB_PATH):
    """
    Performs RFM Customer Segmentation using StandardScaler + K-Means Clustering,
    analyzes cluster profiles, and assigns business-actionable segment labels.
    """
    print("--- Phase 3: Customer Segmentation (K-Means Clustering) ---")
    if not Path(input_path).exists():
        raise FileNotFoundError(f"Customer features file not found at {input_path}.")

    df = pd.read_csv(input_path)

    # Features used for clustering
    rfm_cols = ['Recency', 'Frequency', 'Monetary']
    X = df[rfm_cols].copy()

    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Fit K-Means
    kmeans = KMeans(n_clusters=N_CLUSTERS, random_state=RANDOM_STATE, n_init=10)
    df['Cluster'] = kmeans.fit_predict(X_scaled)

    # Save scaler and model
    joblib.dump(scaler, SCALER_PATH)
    joblib.dump(kmeans, CLUSTERING_MODEL_PATH)
    print(f"Saved StandardScaler to {SCALER_PATH} and KMeans model to {CLUSTERING_MODEL_PATH}")

    # Profile clusters to assign meaningful business labels based on centroids
    cluster_profiles = df.groupby('Cluster')[rfm_cols].mean()
    print("\nCluster Centroid Profiles (Unscaled Means):")
    print(cluster_profiles)

    # Assign business labels dynamically based on composite RFM score
    # Score = Monetary rank + Frequency rank - Recency rank
    cluster_profiles['Monetary_Rank'] = cluster_profiles['Monetary'].rank(ascending=True)
    cluster_profiles['Frequency_Rank'] = cluster_profiles['Frequency'].rank(ascending=True)
    cluster_profiles['Recency_Rank'] = cluster_profiles['Recency'].rank(ascending=False) # lower recency is better
    cluster_profiles['Composite_Score'] = (
        cluster_profiles['Monetary_Rank'] * 0.4 +
        cluster_profiles['Frequency_Rank'] * 0.4 +
        cluster_profiles['Recency_Rank'] * 0.2
    )

    sorted_clusters = cluster_profiles.sort_values(by='Composite_Score', ascending=False).index.tolist()

    label_names = ['High-Value VIPs', 'Loyal Regulars', 'Occasional Buyers', 'At-Risk / Inactive']
    cluster_label_map = {sorted_clusters[i]: label_names[i] for i in range(N_CLUSTERS)}

    df['CustomerSegment'] = df['Cluster'].map(cluster_label_map)

    print("\nAssigned Customer Segment Distribution:")
    segment_counts = df['CustomerSegment'].value_counts()
    for seg, count in segment_counts.items():
        pct = (count / len(df)) * 100
        print(f"  - {seg}: {count} customers ({pct:.1f}%)")

    # Save output dataset
    output_cols = ['CustomerID', 'Recency', 'Frequency', 'Monetary', 'AvgOrderValue', 
                   'TotalProducts', 'UniqueCategories', 'PrimaryCategory', 'Country', 
                   'Cluster', 'CustomerSegment']
    df_output = df[output_cols].copy()
    df_output.to_csv(output_path, index=False)
    print(f"\nCustomer segments saved to: {output_path}")

    # Store in SQLite DB
    conn = sqlite3.connect(db_path)
    df_output.to_sql('customer_segments', conn, if_exists='replace', index=False)
    conn.commit()
    conn.close()
    print(f"Customer segments saved to SQLite DB table 'customer_segments'.")

    return df_output

if __name__ == "__main__":
    run_customer_segmentation()
