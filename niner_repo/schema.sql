-- Drop existing tables
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS expenses;
DROP TABLE IF EXISTS income;
DROP TABLE IF EXISTS income_category;
DROP TABLE IF EXISTS weekly_budgets;
DROP TABLE IF EXISTS budget_categories;
DROP TABLE IF EXISTS budget_allocations;

-- Users table (enhanced from your basic version)
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT 1
);

-- Transactions table (enhanced with category column)
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    transaction_type VARCHAR(20) NOT NULL CHECK (transaction_type IN ('income', 'expense')),
    category VARCHAR(50),  -- Added category column
    category_id INTEGER,
    amount DECIMAL(10, 2) NOT NULL CHECK (amount > 0),
    description TEXT NOT NULL,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Expenses table (separate from transactions for better organization)
CREATE TABLE expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    category VARCHAR(50) NOT NULL CHECK (category IN ('food', 'transportation', 'entertainment', 'other')),
    amount DECIMAL(10, 2) NOT NULL CHECK (amount > 0),
    description TEXT NOT NULL,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    is_recurring BOOLEAN NOT NULL DEFAULT 0,
    recurrence_period VARCHAR(20) CHECK (
        recurrence_period IS NULL OR 
        recurrence_period IN ('daily', 'weekly', 'biweekly', 'monthly', 'quarterly', 'annually')
    ),
    next_recurrence_date DATE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    created_by INTEGER NOT NULL,
    updated_by INTEGER,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (created_by) REFERENCES users (id),
    FOREIGN KEY (updated_by) REFERENCES users (id)
);

-- Income Categories Table
DROP TABLE IF EXISTS income_category;
CREATE TABLE income_category (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    FOREIGN KEY (created_by) REFERENCES users (id),
    UNIQUE(name)
);

-- Create default income categories
INSERT INTO income_category (name, description, created_by) VALUES
('Salary', 'Regular employment income', 1),
('Freelance', 'Income from freelance work', 1),
('Investment', 'Income from investments', 1),
('Business', 'Business income', 1),
('Rental', 'Rental property income', 1),
('Other', 'Other sources of income', 1);

-- Income Table
DROP TABLE IF EXISTS income;
CREATE TABLE income (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    amount DECIMAL(10, 2) NOT NULL CHECK (amount > 0),
    source VARCHAR(100) NOT NULL,
    description TEXT,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    is_recurring BOOLEAN NOT NULL DEFAULT 0,
    recurrence_period VARCHAR(20) CHECK (
        recurrence_period IS NULL OR 
        recurrence_period IN ('daily', 'weekly', 'biweekly', 'monthly', 'quarterly', 'annually')
    ),
    next_recurrence_date DATE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    created_by INTEGER NOT NULL,
    updated_by INTEGER,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (category_id) REFERENCES income_category (id),
    FOREIGN KEY (created_by) REFERENCES users (id),
    FOREIGN KEY (updated_by) REFERENCES users (id)
);

-- Weekly budgets table
CREATE TABLE IF NOT EXISTS weekly_budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    week_start DATE NOT NULL,
    week_end DATE NOT NULL,
    total_budget DECIMAL(10,2) NOT NULL,
    food_budget DECIMAL(10,2) NOT NULL DEFAULT 0,
    transportation_budget DECIMAL(10,2) NOT NULL DEFAULT 0,
    entertainment_budget DECIMAL(10,2) NOT NULL DEFAULT 0,
    other_budget DECIMAL(10,2) NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    UNIQUE(user_id, week_start)
);

-- Create indexes for better query performance
CREATE INDEX idx_income_user_date ON income(user_id, date);
CREATE INDEX idx_income_category ON income(category_id);
CREATE INDEX idx_income_recurring ON income(is_recurring, next_recurrence_date) 
    WHERE is_recurring = 1;
CREATE INDEX idx_income_source ON income(source);
CREATE INDEX idx_transactions_category ON transactions(category);
CREATE INDEX idx_transactions_user_type ON transactions(user_id, transaction_type);
CREATE INDEX idx_transactions_date ON transactions(date);

-- Create trigger to update the updated_at timestamp
CREATE TRIGGER income_update_timestamp
AFTER UPDATE ON income
BEGIN
    UPDATE income 
    SET updated_at = CURRENT_TIMESTAMP,
        updated_by = NEW.updated_by
    WHERE id = NEW.id;
END;

-- Create trigger to validate recurrence data
CREATE TRIGGER income_recurrence_validation
BEFORE INSERT ON income
BEGIN
    SELECT
        CASE
            WHEN NEW.is_recurring = 1 AND NEW.recurrence_period IS NULL
            THEN RAISE(ABORT, 'Recurrence period is required for recurring income')
            WHEN NEW.is_recurring = 1 AND NEW.next_recurrence_date IS NULL
            THEN RAISE(ABORT, 'Next recurrence date is required for recurring income')
            WHEN NEW.is_recurring = 0 AND (NEW.recurrence_period IS NOT NULL OR NEW.next_recurrence_date IS NOT NULL)
            THEN RAISE(ABORT, 'Recurrence fields must be NULL for non-recurring income')
        END;
END;

-- Budget Categories Table
CREATE TABLE budget_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name VARCHAR(50) NOT NULL,
    description TEXT,
    allocation_percentage DECIMAL(5,2) DEFAULT 0 CHECK (allocation_percentage >= 0 AND allocation_percentage <= 100),
    monthly_limit DECIMAL(10,2),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Budget Allocations Table
CREATE TABLE budget_allocations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    allocated_amount DECIMAL(10,2) NOT NULL DEFAULT 0,
    spent_amount DECIMAL(10,2) NOT NULL DEFAULT 0,
    month_year VARCHAR(7) NOT NULL, -- Format: YYYY-MM
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    updated_by INTEGER,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (category_id) REFERENCES budget_categories (id),
    FOREIGN KEY (updated_by) REFERENCES users (id),
    UNIQUE(user_id, category_id, month_year)
);    

-- Insert default admin user
INSERT INTO user (username, email, password) VALUES 
('admin', 'admin@ninerfinance.com', 'pbkdf2:sha256:260000$YourHashedPasswordHere');


-- Create view for active income records
CREATE VIEW v_active_income AS
SELECT 
    i.id,
    i.user_id,
    u.username,
    i.category_id,
    ic.name as category_name,
    i.amount,
    i.source,
    i.description,
    i.date,
    i.is_recurring,
    i.recurrence_period,
    i.next_recurrence_date,
    i.created_at,
    i.updated_at,
    creator.username as created_by_username,
    updater.username as updated_by_username
FROM income i
JOIN user u ON i.user_id = u.id
JOIN income_category ic ON i.category_id = ic.id
JOIN user creator ON i.created_by = creator.id
LEFT JOIN user updater ON i.updated_by = updater.id
WHERE i.is_active = 1 AND ic.is_active = 1;

CREATE VIEW v_active_expenses AS
SELECT 
    e.id,
    e.user_id,
    u.username,
    e.category,
    e.amount,
    e.description,
    e.date,
    e.is_recurring,
    e.recurrence_period,
    e.next_recurrence_date,
    e.created_at,
    e.updated_at,
    creator.username as created_by_username,
    updater.username as updated_by_username
FROM expenses e
JOIN user u ON e.user_id = u.id
JOIN user creator ON e.created_by = creator.id
LEFT JOIN user updater ON e.updated_by = updater.id
WHERE e.is_active = 1;

CREATE VIEW v_all_transactions AS
SELECT 
    'income' as type,
    i.id,
    i.user_id,
    i.amount,
    i.source as description,
    ic.name as category,
    i.date,
    i.created_at
FROM income i
JOIN income_category ic ON i.category_id = ic.id
WHERE i.is_active = 1
UNION ALL
SELECT 
    'expense' as type,
    e.id,
    e.user_id,
    e.amount,
    e.description,
    e.category,
    e.date,
    e.created_at
FROM expenses e
WHERE e.is_active = 1
ORDER BY date DESC, created_at DESC;