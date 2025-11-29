-- Budget Categories Table
DROP TABLE IF EXISTS budget_categories;
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
    FOREIGN KEY (user_id) REFERENCES user (id),
    FOREIGN KEY (created_by) REFERENCES user (id),
    FOREIGN KEY (updated_by) REFERENCES user (id)
);

-- Create index for budget categories
CREATE INDEX idx_budget_categories_user ON budget_categories(user_id, is_active);

-- Budget Allocations Table
DROP TABLE IF EXISTS budget_allocations;
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
    FOREIGN KEY (user_id) REFERENCES user (id),
    FOREIGN KEY (category_id) REFERENCES budget_categories (id),
    FOREIGN KEY (created_by) REFERENCES user (id),
    FOREIGN KEY (updated_by) REFERENCES user (id),
    UNIQUE(user_id, category_id, month_year)
);

-- Create index for budget allocations
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

-- Create trigger to validate total allocation percentage
CREATE TRIGGER validate_budget_allocation_percentage
BEFORE INSERT ON budget_categories
BEGIN
    SELECT CASE
        WHEN (
            SELECT SUM(allocation_percentage) 
            FROM budget_categories 
            WHERE user_id = NEW.user_id AND is_active = 1
        ) + NEW.allocation_percentage > 100
        THEN RAISE(ABORT, 'Total budget allocation percentage cannot exceed 100%')
    END;
END;

-- Create trigger to update budget allocations when income changes
CREATE TRIGGER update_budget_on_income_change
AFTER INSERT ON income
BEGIN
    INSERT INTO budget_allocations (
        user_id,
        category_id,
        allocated_amount,
        month_year,
        created_by,
        is_active
    )
    SELECT 
        NEW.user_id,
        bc.id,
        (NEW.amount * bc.allocation_percentage / 100),
        date(NEW.date, 'start of month'),
        NEW.user_id,
        1
    FROM budget_categories bc
    WHERE bc.user_id = NEW.user_id AND bc.is_active = 1
    ON CONFLICT(user_id, category_id, month_year) 
    DO UPDATE SET 
        allocated_amount = allocated_amount + (NEW.amount * bc.allocation_percentage / 100),
        updated_at = CURRENT_TIMESTAMP,
        updated_by = NEW.user_id;
END;