-- Customer Intelligence & RFM Segmentation Analytics Queries

-- 1. Top 10 High-Value Customers by Total Spend
SELECT 
    CustomerID,
    Country,
    COUNT(DISTINCT TransactionID) AS TotalOrders,
    SUM(Revenue) AS TotalMonetarySpend,
    ROUND(AVG(Revenue), 2) AS AvgOrderValue,
    MAX(TransactionDate) AS LastPurchaseDate
FROM transactions
GROUP BY CustomerID, Country
ORDER BY TotalMonetarySpend DESC
LIMIT 10;

-- 2. Customer RFM Metric Calculation Query
WITH ReferenceDate AS (
    SELECT MAX(DATE(TransactionDate, '+1 day')) AS SnapDate FROM transactions
)
SELECT 
    t.CustomerID,
    CAST((JULIANDAY((SELECT SnapDate FROM ReferenceDate)) - JULIANDAY(MAX(t.TransactionDate))) AS INT) AS RecencyDays,
    COUNT(DISTINCT t.TransactionID) AS FrequencyOrders,
    ROUND(SUM(t.Revenue), 2) AS MonetarySpend,
    ROUND(SUM(t.Revenue) / COUNT(DISTINCT t.TransactionID), 2) AS AvgOrderValue
FROM transactions t
GROUP BY t.CustomerID
ORDER BY MonetarySpend DESC;

-- 3. Customer Segment Breakdown & Revenue Contribution
SELECT 
    cs.CustomerSegment,
    COUNT(cs.CustomerID) AS CustomerCount,
    ROUND(SUM(cs.Monetary), 2) AS TotalSegmentRevenue,
    ROUND(AVG(cs.Monetary), 2) AS AvgSpendPerCustomer,
    ROUND(AVG(cs.Recency), 1) AS AvgRecencyDays
FROM customer_segments cs
GROUP BY cs.CustomerSegment
ORDER BY TotalSegmentRevenue DESC;

-- 4. High-Risk Churn Customer Action List
SELECT 
    cp.CustomerID,
    cp.CustomerSegment,
    cp.RiskCategory,
    cp.ChurnProbability,
    cp.Monetary AS LifetimeValue,
    cp.PrimaryCategory,
    cp.Country
FROM churn_predictions cp
JOIN customer_segments cs ON cp.CustomerID = cs.CustomerID
WHERE cp.RiskCategory = 'High Risk'
ORDER BY cp.Monetary DESC
LIMIT 20;
