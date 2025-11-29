-- Financial Priorities Schema

CREATE TABLE IF NOT EXISTS user_priorities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    priority_type VARCHAR(50) NOT NULL,
    importance_level INTEGER DEFAULT 1,
    target_amount DECIMAL(10, 2),
    target_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS priority_suggestions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    priority_type VARCHAR(50) NOT NULL,
    suggestion_text TEXT NOT NULL,
    category VARCHAR(50),
    min_amount DECIMAL(10, 2),
    max_amount DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_priority_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    priority_id INTEGER NOT NULL,
    action_taken VARCHAR(100),
    action_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (priority_id) REFERENCES user_priorities(id) ON DELETE CASCADE
);

-- Insert default suggestions for each priority type
INSERT INTO priority_suggestions (priority_type, suggestion_text, category, min_amount, max_amount) VALUES
-- Save More suggestions
('Save More', 'Set up automatic transfers to savings account', 'automation', 50, 500),
('Save More', 'Reduce dining out expenses by 20%', 'spending', 100, 300),
('Save More', 'Cancel unused subscriptions', 'subscriptions', 10, 100),
('Save More', 'Build an emergency fund covering 3-6 months of expenses', 'emergency', 3000, 15000),
('Save More', 'Use the 50/30/20 budgeting rule', 'budgeting', NULL, NULL),

-- Reduce Debt suggestions
('Reduce Debt', 'Use the debt avalanche method - pay off highest interest debt first', 'strategy', NULL, NULL),
('Reduce Debt', 'Make bi-weekly payments instead of monthly', 'payments', 100, 1000),
('Reduce Debt', 'Consider debt consolidation for high-interest loans', 'consolidation', 1000, 50000),
('Reduce Debt', 'Allocate windfalls (bonuses, tax refunds) to debt payoff', 'strategy', NULL, NULL),
('Reduce Debt', 'Negotiate lower interest rates with creditors', 'negotiation', NULL, NULL),

-- Invest More suggestions
('Invest More', 'Max out your employer 401(k) match', 'retirement', 500, 19500),
('Invest More', 'Open a Roth IRA and contribute regularly', 'retirement', 100, 6500),
('Invest More', 'Start investing in low-cost index funds', 'investing', 100, 10000),
('Invest More', 'Increase retirement contributions by 1% annually', 'retirement', NULL, NULL),
('Invest More', 'Diversify portfolio across different asset classes', 'strategy', NULL, NULL),

-- Control Spending suggestions
('Control Spending', 'Track every expense for 30 days', 'tracking', NULL, NULL),
('Control Spending', 'Set category budgets and stick to them', 'budgeting', NULL, NULL),
('Control Spending', 'Implement the 24-hour rule for non-essential purchases', 'habits', 50, NULL),
('Control Spending', 'Use cash envelopes for variable expenses', 'budgeting', 200, 1000),
('Control Spending', 'Review and cut recurring expenses monthly', 'subscriptions', 10, 200);

CREATE INDEX IF NOT EXISTS idx_user_priorities_user_id ON user_priorities(user_id);
CREATE INDEX IF NOT EXISTS idx_priority_suggestions_type ON priority_suggestions(priority_type);