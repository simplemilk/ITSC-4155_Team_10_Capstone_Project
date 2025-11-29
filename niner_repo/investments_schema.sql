-- Investments schema
-- Tables: asset_types, investments, positions, investment_transactions

PRAGMA foreign_keys = ON;

-- Asset types (equity, bond, crypto, cash, etf, etc.)
CREATE TABLE IF NOT EXISTS asset_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Investments (a canonical definition of an asset / ticker)
CREATE TABLE IF NOT EXISTS investments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    name TEXT NOT NULL,
    asset_type_id INTEGER NOT NULL,
    exchange TEXT,
    currency TEXT DEFAULT 'USD',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (ticker, exchange),
    FOREIGN KEY (asset_type_id) REFERENCES asset_types (id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_investments_ticker ON investments(ticker);

-- Positions: the current holding per user + instrument (cached current qty and avg cost)
CREATE TABLE IF NOT EXISTS positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    investment_id INTEGER NOT NULL,
    quantity REAL NOT NULL DEFAULT 0,
    avg_cost REAL NOT NULL DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user (id) ON DELETE CASCADE,
    FOREIGN KEY (investment_id) REFERENCES investments (id) ON DELETE CASCADE,
    UNIQUE (user_id, investment_id)
);

CREATE INDEX IF NOT EXISTS idx_positions_user ON positions(user_id);

-- Investment transactions (buys, sells, dividends, splits, fees)
CREATE TABLE IF NOT EXISTS investment_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    investment_id INTEGER NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('buy','sell','dividend','fee','split','transfer')),
    quantity REAL NOT NULL,
    price REAL NOT NULL,
    fees REAL DEFAULT 0,
    total REAL NOT NULL, -- computed: quantity * price +/- fees
    date DATE NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user (id) ON DELETE CASCADE,
    FOREIGN KEY (investment_id) REFERENCES investments (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_invtx_user ON investment_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_invtx_investment ON investment_transactions(investment_id);
