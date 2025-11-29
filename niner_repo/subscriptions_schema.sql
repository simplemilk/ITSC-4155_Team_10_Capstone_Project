-- Subscriptions and Recurring Payments Schema

CREATE TABLE IF NOT EXISTS subscriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    amount REAL NOT NULL,
    currency TEXT DEFAULT 'USD',
    frequency TEXT NOT NULL, -- 'daily', 'weekly', 'monthly', 'yearly'
    category TEXT,
    next_billing_date TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT, -- NULL for ongoing subscriptions
    is_active INTEGER DEFAULT 1,
    auto_detected INTEGER DEFAULT 0, -- 1 if automatically detected from transactions
    transaction_id INTEGER, -- Link to the transaction that created this
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user (id) ON DELETE CASCADE,
    FOREIGN KEY (transaction_id) REFERENCES transactions (id) ON DELETE SET NULL
);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_next_billing ON subscriptions(next_billing_date);
CREATE INDEX IF NOT EXISTS idx_subscriptions_active ON subscriptions(is_active);

-- Subscription categories lookup
CREATE TABLE IF NOT EXISTS subscription_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    icon TEXT,
    color TEXT
);

-- Default categories
INSERT OR IGNORE INTO subscription_categories (name, icon, color) VALUES
('Streaming', 'fa-tv', '#e74c3c'),
('Music', 'fa-music', '#9b59b6'),
('Software', 'fa-laptop-code', '#3498db'),
('Gaming', 'fa-gamepad', '#e67e22'),
('Fitness', 'fa-dumbbell', '#27ae60'),
('News', 'fa-newspaper', '#34495e'),
('Cloud Storage', 'fa-cloud', '#1abc9c'),
('Utilities', 'fa-bolt', '#f39c12'),
('Insurance', 'fa-shield-alt', '#16a085'),
('Other', 'fa-ellipsis-h', '#95a5a6');