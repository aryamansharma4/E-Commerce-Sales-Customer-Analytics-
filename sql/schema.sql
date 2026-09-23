-- E-Commerce Customer Intelligence & Sales Analytics Database Schema
-- Compatible with SQLite, MySQL, and PostgreSQL

-- 1. Raw / Cleaned Transactions Table
CREATE TABLE IF NOT EXISTS transactions (
    TransactionID VARCHAR(50) PRIMARY KEY,
    CustomerID VARCHAR(50) NOT NULL,
    ProductID VARCHAR(50) NOT NULL,
    ProductCategory VARCHAR(100) NOT NULL,
    Quantity INT NOT NULL,
    UnitPrice DECIMAL(10, 2) NOT NULL,
    Revenue DECIMAL(10, 2) NOT NULL,
    TransactionDate DATETIME NOT NULL,
    Country VARCHAR(100),
    PaymentMethod VARCHAR(50)
);

CREATE INDEX IF NOT EXISTS idx_transactions_customer ON transactions(CustomerID);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(TransactionDate);
CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(ProductCategory);

-- 2. Customer Engineered Features Table
CREATE TABLE IF NOT EXISTS customer_features (
    CustomerID VARCHAR(50) PRIMARY KEY,
    LastPurchaseDate DATETIME,
    FirstPurchaseDate DATETIME,
    Recency INT,
    Frequency INT,
    Monetary DECIMAL(10, 2),
    AvgOrderValue DECIMAL(10, 2),
    TotalProducts INT,
    UniqueCategories INT,
    CustomerTenureDays INT,
    AvgDaysBetweenOrders DECIMAL(10, 1),
    PrimaryCategory VARCHAR(100),
    PreferredPaymentMethod VARCHAR(50),
    Country VARCHAR(100)
);

-- 3. Customer Segments (K-Means Results) Table
CREATE TABLE IF NOT EXISTS customer_segments (
    CustomerID VARCHAR(50) PRIMARY KEY,
    Recency INT,
    Frequency INT,
    Monetary DECIMAL(10, 2),
    AvgOrderValue DECIMAL(10, 2),
    Cluster INT,
    CustomerSegment VARCHAR(100),
    FOREIGN KEY (CustomerID) REFERENCES customer_features(CustomerID)
);

-- 4. Churn Predictions Table
CREATE TABLE IF NOT EXISTS churn_predictions (
    CustomerID VARCHAR(50) PRIMARY KEY,
    Recency INT,
    Frequency INT,
    Monetary DECIMAL(10, 2),
    AvgOrderValue DECIMAL(10, 2),
    PrimaryCategory VARCHAR(100),
    Country VARCHAR(100),
    Churn INT,
    ChurnProbability DECIMAL(5, 4),
    RiskCategory VARCHAR(50),
    FOREIGN KEY (CustomerID) REFERENCES customer_features(CustomerID)
);

-- 5. Sales Forecasts Table
CREATE TABLE IF NOT EXISTS sales_forecasts (
    Date DATE PRIMARY KEY,
    ActualRevenue DECIMAL(10, 2),
    OrderVolume INT,
    UnitsSold INT,
    PredictedRevenue DECIMAL(10, 2),
    LowerBound DECIMAL(10, 2),
    UpperBound DECIMAL(10, 2),
    DataType VARCHAR(20)
);
