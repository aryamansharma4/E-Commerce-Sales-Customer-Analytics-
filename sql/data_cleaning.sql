-- Data Cleaning & Validation Queries

-- 1. Identify and remove duplicate transaction records
SELECT TransactionID, CustomerID, TransactionDate, COUNT(*) as DupCount
FROM transactions
GROUP BY TransactionID, CustomerID, TransactionDate
HAVING COUNT(*) > 1;

-- 2. Identify records with invalid prices or quantities
SELECT *
FROM transactions
WHERE Quantity <= 0 OR UnitPrice <= 0;

-- 3. Identify transactions missing CustomerID
SELECT *
FROM transactions
WHERE CustomerID IS NULL OR CustomerID = '';

-- 4. Calculate total gross revenue after cleaning
SELECT 
    COUNT(DISTINCT TransactionID) AS TotalCleanTransactions,
    COUNT(DISTINCT CustomerID) AS TotalUniqueCustomers,
    SUM(Quantity * UnitPrice) AS TotalCalculatedRevenue,
    SUM(Revenue) AS TotalStoredRevenue
FROM transactions;
