-- Sales & Financial Performance Analytics Queries

-- 1. Monthly Revenue & Order Volume Growth Trend
SELECT 
    STRFTIME('%Y-%m', TransactionDate) AS YearMonth,
    COUNT(DISTINCT TransactionID) AS TotalOrders,
    COUNT(DISTINCT CustomerID) AS ActiveCustomers,
    SUM(Quantity) AS TotalUnitsSold,
    ROUND(SUM(Revenue), 2) AS GrossRevenue,
    ROUND(AVG(Revenue), 2) AS AverageOrderValue
FROM transactions
GROUP BY YearMonth
ORDER BY YearMonth ASC;

-- 2. Product Category Performance Breakdown
SELECT 
    ProductCategory,
    COUNT(DISTINCT TransactionID) AS TotalOrders,
    SUM(Quantity) AS TotalUnitsSold,
    ROUND(SUM(Revenue), 2) AS GrossRevenue,
    ROUND((SUM(Revenue) * 100.0 / (SELECT SUM(Revenue) FROM transactions)), 2) AS RevenueSharePct
FROM transactions
GROUP BY ProductCategory
ORDER BY GrossRevenue DESC;

-- 3. Payment Method & Geographic Revenue Distribution
SELECT 
    Country,
    PaymentMethod,
    COUNT(DISTINCT CustomerID) AS UniqueCustomers,
    COUNT(DISTINCT TransactionID) AS TotalTransactions,
    ROUND(SUM(Revenue), 2) AS TotalRevenue
FROM transactions
GROUP BY Country, PaymentMethod
ORDER BY TotalRevenue DESC;

-- 4. Daily Sales & Moving Average (Last 30 Days)
WITH DailySales AS (
    SELECT 
        DATE(TransactionDate) AS SalesDate,
        SUM(Revenue) AS DailyRevenue
    FROM transactions
    GROUP BY SalesDate
)
SELECT 
    SalesDate,
    DailyRevenue,
    ROUND(AVG(DailyRevenue) OVER (ORDER BY SalesDate ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 2) AS 7DayMovingAvgRevenue
FROM DailySales
ORDER BY SalesDate DESC
LIMIT 30;
