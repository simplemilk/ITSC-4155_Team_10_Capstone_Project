-- Drop existing tables
DROP VIEW IF EXISTS v_budget_status;
DROP TABLE IF EXISTS budget_allocations;
DROP TABLE IF EXISTS budget_categories;
DROP TABLE IF EXISTS budgets;

-- Budgets Table (Weekly budget tracking)
CREATE TABLE budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL DEFAULT 0,
    food_budget DECIMAL(10,2) NOT NULL DEFAULT 0,
    transportation_budget DECIMAL(10,2) NOT NULL DEFAULT 0,
    entertainment_budget DECIMAL(10,2) NOT NULL DEFAULT 0,
    other_budget DECIMAL(10,2) NOT NULL DEFAULT 0,
    week_start_date DATE NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_budgets_user ON budgets(user_id);
CREATE INDEX idx_budgets_week ON budgets(week_start_date);
CREATE UNIQUE INDEX idx_budgets_user_week ON budgets(user_id, week_start_date);

-- Budget Categories Table
CREATE TABLE budget_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name VARCHAR(50) NOT NULL,
    description TEXT,
    allocation_percentage DECIMAL(5,2) NOT NULL CHECK (
        allocation_percentage >= 0 AND 
        allocation_percentage <= 100
    ),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    created_by INTEGER NOT NULL,
    updated_by INTEGER,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (updated_by) REFERENCES users(id)
);

CREATE INDEX idx_budget_categories_user ON budget_categories(user_id, is_active);

-- Budget Allocations Table
CREATE TABLE budget_allocations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    allocated_amount DECIMAL(10,2) NOT NULL CHECK (allocated_amount >= 0),
    month_year DATE NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    created_by INTEGER NOT NULL,
    updated_by INTEGER,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (category_id) REFERENCES budget_categories(id),
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (updated_by) REFERENCES users(id),
    UNIQUE(user_id, category_id, month_year)
);

CREATE INDEX idx_budget_allocations_user_month 
ON budget_allocations(user_id, month_year, is_active);

-- Create view for current budget status
CREATE VIEW v_budget_status AS
SELECT 
    ba.user_id,
    bc.id as category_id,
    bc.name as category_name,
    ba.month_year,
    ba.allocated_amount,
    COALESCE(SUM(e.amount), 0) as spent_amount,
    ba.allocated_amount - COALESCE(SUM(e.amount), 0) as remaining_amount,
    (COALESCE(SUM(e.amount), 0) / ba.allocated_amount * 100) as usage_percentage
FROM budget_allocations ba
JOIN budget_categories bc ON ba.category_id = bc.id
LEFT JOIN expenses e ON e.category_id = bc.id 
    AND e.user_id = ba.user_id 
    AND strftime('%Y-%m', e.date) = strftime('%Y-%m', ba.month_year)
    AND e.is_active = 1
WHERE ba.is_active = 1 AND bc.is_active = 1
GROUP BY ba.user_id, bc.id, bc.name, ba.month_year, ba.allocated_amount;