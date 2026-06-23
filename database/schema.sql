-- ============================================================================
-- STOCK MARKET PORTFOLIO & ANALYSIS SYSTEM
-- Database: MySQL 8.0+
-- File: schema.sql
-- Description: Complete normalized schema (3NF) for the DBMS mini project
-- ============================================================================

DROP DATABASE IF EXISTS stock_portfolio_db;
CREATE DATABASE stock_portfolio_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE stock_portfolio_db;

-- ----------------------------------------------------------------------------
-- TABLE: sectors
-- Master table for industry sectors (e.g., Technology, Banking, Energy)
-- Separated out to avoid repeating sector text on every stock row (2NF/3NF)
-- ----------------------------------------------------------------------------
CREATE TABLE sectors (
    sector_id     INT AUTO_INCREMENT PRIMARY KEY,
    sector_name   VARCHAR(100) NOT NULL UNIQUE,
    description   VARCHAR(255) DEFAULT NULL,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- TABLE: users
-- Stores registered users (both normal users and admins via role flag)
-- ----------------------------------------------------------------------------
CREATE TABLE users (
    user_id        INT AUTO_INCREMENT PRIMARY KEY,
    full_name      VARCHAR(100)  NOT NULL,
    email          VARCHAR(120)  NOT NULL UNIQUE,
    username       VARCHAR(50)   NOT NULL UNIQUE,
    password_hash  VARCHAR(255)  NOT NULL,
    role           ENUM('user', 'admin') NOT NULL DEFAULT 'user',
    virtual_balance DECIMAL(15,2) NOT NULL DEFAULT 1000000.00,  -- starting virtual cash
    is_active      TINYINT(1) NOT NULL DEFAULT 1,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_users_email (email),
    INDEX idx_users_username (username)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- TABLE: stocks
-- Master table of stocks available on the platform.
-- sector_id is a foreign key -> sectors (removes transitive dependency,
-- satisfies 3NF: sector_name/description don't repeat per stock)
-- ----------------------------------------------------------------------------
CREATE TABLE stocks (
    stock_id       INT AUTO_INCREMENT PRIMARY KEY,
    ticker_symbol  VARCHAR(20)   NOT NULL UNIQUE,   -- e.g. AAPL, INFY.NS
    company_name   VARCHAR(150)  NOT NULL,
    sector_id      INT           DEFAULT NULL,
    exchange       VARCHAR(20)   DEFAULT NULL,       -- NASDAQ, NSE, BSE etc.
    currency       VARCHAR(10)   DEFAULT 'USD',
    last_price     DECIMAL(15,4) DEFAULT 0.0000,
    last_updated   TIMESTAMP     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active      TINYINT(1)    NOT NULL DEFAULT 1,
    created_at     TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_stocks_sector
        FOREIGN KEY (sector_id) REFERENCES sectors(sector_id)
        ON DELETE SET NULL ON UPDATE CASCADE,

    INDEX idx_stocks_ticker (ticker_symbol),
    INDEX idx_stocks_sector (sector_id)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- TABLE: portfolio
-- Holds the CURRENT aggregated holding of a user for a given stock.
-- One row per (user, stock) -> avoids partial dependency issues (2NF):
-- quantity & avg_buy_price depend on the FULL key (user_id, stock_id),
-- not on stock_id alone.
-- ----------------------------------------------------------------------------
CREATE TABLE portfolio (
    portfolio_id    INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    stock_id        INT NOT NULL,
    quantity        INT NOT NULL DEFAULT 0,
    average_buy_price DECIMAL(15,4) NOT NULL DEFAULT 0.0000,
    total_invested  DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_portfolio_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_portfolio_stock
        FOREIGN KEY (stock_id) REFERENCES stocks(stock_id)
        ON DELETE CASCADE ON UPDATE CASCADE,

    CONSTRAINT uq_user_stock UNIQUE (user_id, stock_id),
    CONSTRAINT chk_quantity_nonneg CHECK (quantity >= 0),

    INDEX idx_portfolio_user (user_id)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- TABLE: transactions
-- Immutable ledger of every BUY/SELL action. This is the source of truth;
-- 'portfolio' table is a derived/aggregated cache for fast reads.
-- ----------------------------------------------------------------------------
CREATE TABLE transactions (
    transaction_id   INT AUTO_INCREMENT PRIMARY KEY,
    user_id          INT NOT NULL,
    stock_id         INT NOT NULL,
    transaction_type ENUM('BUY', 'SELL') NOT NULL,
    quantity         INT NOT NULL,
    price_per_share  DECIMAL(15,4) NOT NULL,
    total_amount     DECIMAL(15,2) NOT NULL,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_transactions_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_transactions_stock
        FOREIGN KEY (stock_id) REFERENCES stocks(stock_id)
        ON DELETE CASCADE ON UPDATE CASCADE,

    CONSTRAINT chk_txn_quantity_pos CHECK (quantity > 0),
    CONSTRAINT chk_txn_price_pos CHECK (price_per_share >= 0),

    INDEX idx_transactions_user (user_id),
    INDEX idx_transactions_stock (stock_id),
    INDEX idx_transactions_date (transaction_date)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- TABLE: watchlist
-- Stocks a user is tracking but does not necessarily own.
-- ----------------------------------------------------------------------------
CREATE TABLE watchlist (
    watchlist_id   INT AUTO_INCREMENT PRIMARY KEY,
    user_id        INT NOT NULL,
    stock_id       INT NOT NULL,
    added_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_watchlist_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_watchlist_stock
        FOREIGN KEY (stock_id) REFERENCES stocks(stock_id)
        ON DELETE CASCADE ON UPDATE CASCADE,

    CONSTRAINT uq_user_watch_stock UNIQUE (user_id, stock_id),

    INDEX idx_watchlist_user (user_id)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- TABLE: audit_log  (optional but useful for admin "view transactions"
-- and to demonstrate triggers in viva)
-- ----------------------------------------------------------------------------
CREATE TABLE audit_log (
    log_id        INT AUTO_INCREMENT PRIMARY KEY,
    user_id       INT DEFAULT NULL,
    action        VARCHAR(100) NOT NULL,
    details       VARCHAR(255) DEFAULT NULL,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_audit_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ============================================================================
-- VIEWS (useful for dashboard/reporting queries, also good viva talking points)
-- ============================================================================

-- View: current holdings with live computed market value placeholders
CREATE OR REPLACE VIEW vw_portfolio_summary AS
SELECT
    p.portfolio_id,
    p.user_id,
    u.username,
    s.stock_id,
    s.ticker_symbol,
    s.company_name,
    sec.sector_name,
    p.quantity,
    p.average_buy_price,
    p.total_invested,
    s.last_price,
    ROUND(p.quantity * s.last_price, 2) AS current_value,
    ROUND((p.quantity * s.last_price) - p.total_invested, 2) AS profit_loss,
    CASE WHEN p.total_invested > 0
         THEN ROUND((((p.quantity * s.last_price) - p.total_invested) / p.total_invested) * 100, 2)
         ELSE 0 END AS profit_loss_percent
FROM portfolio p
JOIN users u ON u.user_id = p.user_id
JOIN stocks s ON s.stock_id = p.stock_id
LEFT JOIN sectors sec ON sec.sector_id = s.sector_id
WHERE p.quantity > 0;

-- View: per-user dashboard aggregate
CREATE OR REPLACE VIEW vw_user_dashboard AS
SELECT
    p.user_id,
    SUM(p.total_invested) AS total_investment,
    SUM(p.quantity * s.last_price) AS current_value,
    SUM(p.quantity * s.last_price) - SUM(p.total_invested) AS total_profit_loss
FROM portfolio p
JOIN stocks s ON s.stock_id = p.stock_id
WHERE p.quantity > 0
GROUP BY p.user_id;

-- View: sector-wise allocation per user (for pie chart query convenience)
CREATE OR REPLACE VIEW vw_sector_allocation AS
SELECT
    p.user_id,
    COALESCE(sec.sector_name, 'Uncategorized') AS sector_name,
    SUM(p.quantity * s.last_price) AS sector_value
FROM portfolio p
JOIN stocks s ON s.stock_id = p.stock_id
LEFT JOIN sectors sec ON sec.sector_id = s.sector_id
WHERE p.quantity > 0
GROUP BY p.user_id, sec.sector_name;

-- ============================================================================
-- TRIGGERS (demonstrates DB-level integrity logic — good for viva)
-- ============================================================================

DELIMITER //

-- Trigger: log every transaction insert into audit_log automatically
CREATE TRIGGER trg_after_transaction_insert
AFTER INSERT ON transactions
FOR EACH ROW
BEGIN
    INSERT INTO audit_log (user_id, action, details)
    VALUES (
        NEW.user_id,
        NEW.transaction_type,
        CONCAT('Stock ID ', NEW.stock_id, ' | Qty: ', NEW.quantity, ' | Price: ', NEW.price_per_share)
    );
END//

DELIMITER ;

-- ============================================================================
-- SAMPLE / SEED DATA
-- ============================================================================

INSERT INTO sectors (sector_name, description) VALUES
('Technology', 'Software, hardware and IT services companies'),
('Banking & Finance', 'Banks, NBFCs and financial institutions'),
('Energy', 'Oil, gas and renewable energy companies'),
('Healthcare', 'Pharma, hospitals and biotech companies'),
('Automobile', 'Auto manufacturers and ancillary companies'),
('Consumer Goods', 'FMCG and retail companies'),
('Telecommunications', 'Telecom service providers');

-- Default admin user. Password = "Admin@123" (hashed at app startup via seed script;
-- placeholder hash below is regenerated by backend/seed.py using werkzeug.security)
INSERT INTO users (full_name, email, username, password_hash, role, virtual_balance)
VALUES ('System Administrator', 'admin@stockportfolio.com', 'admin',
        'PLACEHOLDER_WILL_BE_REPLACED_BY_SEED_SCRIPT', 'admin', 1000000.00);

-- Sample stocks across sectors (last_price values are illustrative seed values;
-- the app refreshes real prices live via yfinance)
INSERT INTO stocks (ticker_symbol, company_name, sector_id, exchange, currency, last_price) VALUES
('AAPL',  'Apple Inc.',                 1, 'NASDAQ', 'USD', 195.00),
('MSFT',  'Microsoft Corporation',      1, 'NASDAQ', 'USD', 420.00),
('GOOGL', 'Alphabet Inc.',              1, 'NASDAQ', 'USD', 175.00),
('TSLA',  'Tesla Inc.',                 5, 'NASDAQ', 'USD', 250.00),
('AMZN',  'Amazon.com Inc.',            6, 'NASDAQ', 'USD', 180.00),
('JPM',   'JPMorgan Chase & Co.',       2, 'NYSE',   'USD', 200.00),
('XOM',   'Exxon Mobil Corporation',    3, 'NYSE',   'USD', 115.00),
('JNJ',   'Johnson & Johnson',          4, 'NYSE',   'USD', 150.00),
('NFLX',  'Netflix Inc.',               1, 'NASDAQ', 'USD', 650.00),
('TCS.NS','Tata Consultancy Services',  1, 'NSE',    'INR', 3800.00),
('RELIANCE.NS','Reliance Industries',   3, 'NSE',    'INR', 2900.00),
('INFY.NS','Infosys Limited',           1, 'NSE',    'INR', 1500.00),
('HDFCBANK.NS','HDFC Bank Limited',     2, 'NSE',    'INR', 1650.00),
('BHARTIARTL.NS','Bharti Airtel Limited',7,'NSE',    'INR', 1400.00);
