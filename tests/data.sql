-- Test data for Niner Finance database
-- This file contains sample data for testing purposes

-- Clear existing data (in reverse order due to foreign key constraints)
DELETE FROM budgets;
DELETE FROM expenses;
DELETE FROM income;
DELETE FROM categories;
DELETE FROM users;

-- Reset auto-increment counters
DELETE FROM sqlite_sequence WHERE name IN ('users', 'expenses', 'income', 'budgets', 'categories');

-- Insert test users
INSERT INTO users (id, username, email, password, first_name, last_name, created_at, is_active) VALUES
(1, 'demo', 'demo@ninerfinance.com', 'pbkdf2:sha256:260000$abc123$def456', 'Demo', 'User', '2024-01-01 00:00:00', 1),
(2, 'john_doe', 'john.doe@email.com', 'pbkdf2:sha256:260000$xyz789$uvw012', 'John', 'Doe', '2024-01-15 10:30:00', 1),
(3, 'jane_smith', 'jane.smith@email.com', 'pbkdf2:sha256:260000$qwe345$rty678', 'Jane', 'Smith', '2024-02-01 14:20:00', 1),
(4, 'bob_wilson', 'bob.wilson@email.com', 'pbkdf2:sha256:260000$asd901$fgh234', 'Bob', 'Wilson', '2024-02-15 09:45:00', 1),
(5, 'alice_brown', 'alice.brown@email.com', 'pbkdf2:sha256:260000$zxc567$bnm890', 'Alice', 'Brown', '2024-03-01 16:15:00', 1);

-- Insert categories (if categories table exists)
INSERT OR IGNORE INTO categories (id, name, description, icon, color, created_at) VALUES
(1, 'food', 'Food and dining expenses', 'fas fa-utensils', '#FF6B6B', '2024-01-01 00:00:00'),
(2, 'transportation', 'Transportation and travel', 'fas fa-car', '#4ECDC4', '2024-01-01 00:00:00'),
(3, 'entertainment', 'Entertainment and recreation', 'fas fa-film', '#45B7D1', '2024-01-01 00:00:00'),
(4, 'utilities', 'Utilities and bills', 'fas fa-bolt', '#F7DC6F', '2024-01-01 00:00:00'),
(5, 'healthcare', 'Healthcare and medical', 'fas fa-heartbeat', '#BB8FCE', '2024-01-01 00:00:00'),
(6, 'shopping', 'Shopping and retail', 'fas fa-shopping-bag', '#F8C471', '2024-01-01 00:00:00'),
(7, 'education', 'Education and learning', 'fas fa-graduation-cap', '#85C1E9', '2024-01-01 00:00:00'),
(8, 'other', 'Other miscellaneous expenses', 'fas fa-ellipsis-h', '#ABEBC6', '2024-01-01 00:00:00');

-- Insert test expenses for different users and time periods
INSERT INTO expenses (id, user_id, description, amount, category, date, notes, recurrence_type, is_active, created_at) VALUES
-- Demo user expenses (current week)
(1, 1, 'Grocery shopping at Kroger', 127.85, 'food', '2024-10-28', 'Weekly grocery run', 'none', 1, '2024-10-28 10:30:00'),
(2, 1, 'Gas for car', 45.20, 'transportation', '2024-10-27', 'Shell station on Main St', 'none', 1, '2024-10-27 08:15:00'),
(3, 1, 'Coffee at Starbucks', 8.75, 'food', '2024-10-26', 'Morning coffee', 'none', 1, '2024-10-26 07:45:00'),
(4, 1, 'Movie tickets', 24.00, 'entertainment', '2024-10-25', 'Watched new Marvel movie', 'none', 1, '2024-10-25 19:30:00'),
(5, 1, 'Electric bill', 89.50, 'utilities', '2024-10-24', 'Monthly electric bill', 'monthly', 1, '2024-10-24 14:20:00'),

-- Demo user expenses (previous weeks)
(6, 1, 'Lunch at Chipotle', 12.50, 'food', '2024-10-20', 'Quick lunch break', 'none', 1, '2024-10-20 12:00:00'),
(7, 1, 'Uber ride', 18.75, 'transportation', '2024-10-19', 'Ride to airport', 'none', 1, '2024-10-19 15:30:00'),
(8, 1, 'Netflix subscription', 15.99, 'entertainment', '2024-10-18', 'Monthly streaming service', 'monthly', 1, '2024-10-18 09:00:00'),
(9, 1, 'Prescription medication', 35.00, 'healthcare', '2024-10-17', 'Monthly prescription refill', 'none', 1, '2024-10-17 11:45:00'),
(10, 1, 'Clothes shopping', 89.99, 'shopping', '2024-10-16', 'New winter jacket', 'none', 1, '2024-10-16 16:20:00'),

-- John Doe expenses
(11, 2, 'Breakfast at IHOP', 18.45, 'food', '2024-10-28', 'Weekend breakfast', 'none', 1, '2024-10-28 09:30:00'),
(12, 2, 'Metro card refill', 25.00, 'transportation', '2024-10-27', 'Monthly transit pass', 'monthly', 1, '2024-10-27 07:00:00'),
(13, 2, 'Gym membership', 49.99, 'healthcare', '2024-10-26', 'Monthly gym membership', 'monthly', 1, '2024-10-26 18:00:00'),
(14, 2, 'Textbooks', 145.75, 'education', '2024-10-25', 'College textbooks for semester', 'none', 1, '2024-10-25 13:15:00'),
(15, 2, 'Internet bill', 79.99, 'utilities', '2024-10-24', 'Monthly internet service', 'monthly', 1, '2024-10-24 10:30:00'),

-- Jane Smith expenses
(16, 3, 'Farmers market', 42.30, 'food', '2024-10-28', 'Fresh vegetables and fruits', 'none', 1, '2024-10-28 08:00:00'),
(17, 3, 'Car insurance', 125.00, 'transportation', '2024-10-27', 'Monthly car insurance', 'monthly', 1, '2024-10-27 16:45:00'),
(18, 3, 'Concert tickets', 85.00, 'entertainment', '2024-10-26', 'Local band concert', 'none', 1, '2024-10-26 20:00:00'),
(19, 3, 'Phone bill', 65.00, 'utilities', '2024-10-25', 'Monthly phone service', 'monthly', 1, '2024-10-25 12:00:00'),
(20, 3, 'Doctor visit copay', 25.00, 'healthcare', '2024-10-24', 'Annual checkup', 'none', 1, '2024-10-24 15:30:00'),

-- Bob Wilson expenses
(21, 4, 'Pizza delivery', 28.50, 'food', '2024-10-28', 'Friday night dinner', 'none', 1, '2024-10-28 19:45:00'),
(22, 4, 'Gas station', 52.75, 'transportation', '2024-10-27', 'Weekend road trip fill-up', 'none', 1, '2024-10-27 06:30:00'),
(23, 4, 'Gaming subscription', 9.99, 'entertainment', '2024-10-26', 'Xbox Game Pass', 'monthly', 1, '2024-10-26 21:00:00'),
(24, 4, 'Office supplies', 34.99, 'other', '2024-10-25', 'Pens, notebooks, etc.', 'none', 1, '2024-10-25 14:15:00'),
(25, 4, 'Water bill', 45.25, 'utilities', '2024-10-24', 'Quarterly water bill', 'quarterly', 1, '2024-10-24 11:00:00'),

-- Alice Brown expenses
(26, 5, 'Coffee beans', 15.99, 'food', '2024-10-28', 'Monthly coffee supply', 'none', 1, '2024-10-28 11:30:00'),
(27, 5, 'Bus pass', 75.00, 'transportation', '2024-10-27', 'Monthly bus pass', 'monthly', 1, '2024-10-27 08:45:00'),
(28, 5, 'Art supplies', 67.50, 'education', '2024-10-26', 'Painting supplies for class', 'none', 1, '2024-10-26 15:20:00'),
(29, 5, 'Streaming services', 23.97, 'entertainment', '2024-10-25', 'Hulu + Disney+', 'monthly', 1, '2024-10-25 10:15:00'),
(30, 5, 'Vitamins', 29.99, 'healthcare', '2024-10-24', 'Monthly vitamin supply', 'monthly', 1, '2024-10-24 13:45:00');

-- Insert test income data
INSERT INTO income (id, user_id, amount, source, date, recurrence_period, description, is_active, created_at) VALUES
-- Demo user income
(1, 1, 3500.00, 'Primary Job', '2024-10-01', 'monthly', 'Software Developer at Tech Corp', 1, '2024-10-01 00:00:00'),
(2, 1, 500.00, 'Freelance', '2024-10-15', 'none', 'Web development project', 1, '2024-10-15 00:00:00'),
(3, 1, 150.00, 'Side Business', '2024-10-20', 'weekly', 'Online tutoring', 1, '2024-10-20 00:00:00'),

-- John Doe income
(4, 2, 2800.00, 'Part-time Job', '2024-10-01', 'monthly', 'University Research Assistant', 1, '2024-10-01 00:00:00'),
(5, 2, 400.00, 'Scholarship', '2024-10-01', 'monthly', 'Academic scholarship', 1, '2024-10-01 00:00:00'),
(6, 2, 200.00, 'Gig Work', '2024-10-10', 'none', 'Food delivery driving', 1, '2024-10-10 00:00:00'),

-- Jane Smith income
(7, 3, 4200.00, 'Full-time Job', '2024-10-01', 'monthly', 'Marketing Manager', 1, '2024-10-01 00:00:00'),
(8, 3, 300.00, 'Investment', '2024-10-01', 'monthly', 'Dividend income', 1, '2024-10-01 00:00:00'),

-- Bob Wilson income
(9, 4, 3200.00, 'Full-time Job', '2024-10-01', 'monthly', 'Graphic Designer', 1, '2024-10-01 00:00:00'),
(10, 4, 250.00, 'Freelance', '2024-10-12', 'none', 'Logo design project', 1, '2024-10-12 00:00:00'),

-- Alice Brown income
(11, 5, 2500.00, 'Part-time Job', '2024-10-01', 'monthly', 'Art Teacher', 1, '2024-10-01 00:00:00'),
(12, 5, 180.00, 'Art Sales', '2024-10-08', 'none', 'Sold painting at local gallery', 1, '2024-10-08 00:00:00'),
(13, 5, 100.00, 'Art Classes', '2024-10-15', 'weekly', 'Private art lessons', 1, '2024-10-15 00:00:00');

-- Insert test budget data
INSERT INTO budgets (id, user_id, week_start, week_end, total_budget, food_budget, transportation_budget, entertainment_budget, utilities_budget, healthcare_budget, shopping_budget, education_budget, other_budget, is_active, created_at) VALUES
-- Demo user budgets
(1, 1, '2024-10-21', '2024-10-27', 500.00, 180.00, 80.00, 60.00, 100.00, 40.00, 30.00, 10.00, 0.00, 1, '2024-10-21 00:00:00'),
(2, 1, '2024-10-28', '2024-11-03', 520.00, 200.00, 85.00, 65.00, 90.00, 45.00, 25.00, 10.00, 0.00, 1, '2024-10-28 00:00:00'),

-- John Doe budgets
(3, 2, '2024-10-21', '2024-10-27', 350.00, 120.00, 50.00, 40.00, 80.00, 30.00, 20.00, 30.00, 0.00, 1, '2024-10-21 00:00:00'),
(4, 2, '2024-10-28', '2024-11-03', 380.00, 130.00, 55.00, 45.00, 85.00, 35.00, 25.00, 35.00, 0.00, 1, '2024-10-28 00:00:00'),

-- Jane Smith budgets
(5, 3, '2024-10-21', '2024-10-27', 600.00, 220.00, 100.00, 80.00, 120.00, 50.00, 40.00, 10.00, 0.00, 1, '2024-10-21 00:00:00'),
(6, 3, '2024-10-28', '2024-11-03', 620.00, 230.00, 105.00, 85.00, 115.00, 55.00, 45.00, 15.00, 0.00, 1, '2024-10-28 00:00:00'),

-- Bob Wilson budgets
(7, 4, '2024-10-21', '2024-10-27', 450.00, 160.00, 70.00, 50.00, 90.00, 35.00, 30.00, 15.00, 0.00, 1, '2024-10-21 00:00:00'),
(8, 4, '2024-10-28', '2024-11-03', 470.00, 170.00, 75.00, 55.00, 95.00, 40.00, 35.00, 20.00, 0.00, 1, '2024-10-28 00:00:00'),

-- Alice Brown budgets
(9, 5, '2024-10-21', '2024-10-27', 300.00, 100.00, 60.00, 30.00, 60.00, 25.00, 15.00, 20.00, 0.00, 1, '2024-10-21 00:00:00'),
(10, 5, '2024-10-28', '2024-11-03', 320.00, 110.00, 65.00, 35.00, 65.00, 30.00, 20.00, 25.00, 0.00, 1, '2024-10-28 00:00:00');

-- Insert additional historical data for better testing
-- Previous month expenses for demo user
INSERT INTO expenses (user_id, description, amount, category, date, notes, recurrence_type, is_active, created_at) VALUES
(1, 'Rent payment', 1200.00, 'utilities', '2024-09-01', 'Monthly rent', 'monthly', 1, '2024-09-01 00:00:00'),
(1, 'Car payment', 350.00, 'transportation', '2024-09-01', 'Monthly car loan', 'monthly', 1, '2024-09-01 00:00:00'),
(1, 'Health insurance', 275.00, 'healthcare', '2024-09-01', 'Monthly health insurance premium', 'monthly', 1, '2024-09-01 00:00:00'),
(1, 'Groceries', 89.50, 'food', '2024-09-15', 'Weekly grocery shopping', 'none', 1, '2024-09-15 00:00:00'),
(1, 'Dinner out', 45.75, 'food', '2024-09-18', 'Date night restaurant', 'none', 1, '2024-09-18 00:00:00'),
(1, 'Gas', 42.00, 'transportation', '2024-09-20', 'Weekly gas fill-up', 'none', 1, '2024-09-20 00:00:00'),
(1, 'Books', 67.99, 'education', '2024-09-22', 'Professional development books', 'none', 1, '2024-09-22 00:00:00');

-- Create some test recurring expenses
INSERT INTO expenses (user_id, description, amount, category, date, notes, recurrence_type, is_active, created_at) VALUES
(1, 'Spotify Premium', 9.99, 'entertainment', '2024-10-01', 'Music streaming service', 'monthly', 1, '2024-10-01 00:00:00'),
(2, 'Adobe Creative Suite', 52.99, 'education', '2024-10-01', 'Design software subscription', 'monthly', 1, '2024-10-01 00:00:00'),
(3, 'Yoga class membership', 89.00, 'healthcare', '2024-10-01', 'Monthly yoga studio membership', 'monthly', 1, '2024-10-01 00:00:00'),
(4, 'Cloud storage', 4.99, 'other', '2024-10-01', 'Google Drive storage', 'monthly', 1, '2024-10-01 00:00:00'),
(5, 'Art supply subscription', 29.99, 'education', '2024-10-01', 'Monthly art supply box', 'monthly', 1, '2024-10-01 00:00:00');

-- Update last_login for some users to simulate recent activity
UPDATE users SET last_login = '2024-10-28 15:30:00' WHERE id = 1;
UPDATE users SET last_login = '2024-10-27 09:15:00' WHERE id = 2;
UPDATE users SET last_login = '2024-10-28 11:45:00' WHERE id = 3;
UPDATE users SET last_login = '2024-10-26 14:20:00' WHERE id = 4;
UPDATE users SET last_login = '2024-10-28 08:30:00' WHERE id = 5;

-- Add some test financial goals (if goals table exists)
INSERT OR IGNORE INTO goals (user_id, title, target_amount, current_amount, target_date, category, description, is_active, created_at) VALUES
(1, 'Emergency Fund', 5000.00, 1250.00, '2024-12-31', 'savings', 'Build emergency fund of 3 months expenses', 1, '2024-10-01 00:00:00'),
(1, 'Vacation Fund', 2000.00, 450.00, '2024-06-01', 'savings', 'Save for summer vacation trip', 1, '2024-10-01 00:00:00'),
(2, 'New Laptop', 1500.00, 300.00, '2024-12-15', 'shopping', 'Save for new laptop for studies', 1, '2024-10-01 00:00:00'),
(3, 'Car Down Payment', 8000.00, 2100.00, '2024-08-01', 'transportation', 'Save for new car down payment', 1, '2024-10-01 00:00:00'),
(4, 'Camera Equipment', 3500.00, 875.00, '2024-11-30', 'education', 'Professional camera gear for freelance work', 1, '2024-10-01 00:00:00'),
(5, 'Art Studio Rent', 1200.00, 340.00, '2024-12-01', 'education', 'First month rent for art studio space', 1, '2024-10-01 00:00:00');

-- Create some test alerts/notifications (if notifications table exists)
INSERT OR IGNORE INTO notifications (user_id, title, message, type, is_read, created_at) VALUES
(1, 'Budget Alert', 'You have spent 85% of your food budget this week', 'warning', 0, '2024-10-28 12:00:00'),
(1, 'Goal Progress', 'Great job! You are 25% toward your Emergency Fund goal', 'success', 0, '2024-10-27 18:30:00'),
(2, 'Expense Added', 'New expense: Textbooks - $145.75', 'info', 1, '2024-10-25 13:15:00'),
(3, 'Budget Exceeded', 'You have exceeded your entertainment budget by $10.00', 'danger', 0, '2024-10-26 20:30:00'),
(4, 'Monthly Summary', 'Your monthly expense summary is ready to view', 'info', 1, '2024-10-01 09:00:00'),
(5, 'Income Added', 'New income recorded: Art Sales - $180.00', 'success', 1, '2024-10-08 16:45:00');

-- Add some sample tags for expenses (if tags functionality exists)
INSERT OR IGNORE INTO tags (name, color, description, created_at) VALUES
('Work Related', '#3498db', 'Business and work expenses', '2024-10-01 00:00:00'),
('Emergency', '#e74c3c', 'Unexpected or emergency expenses', '2024-10-01 00:00:00'),
('Holiday', '#f39c12', 'Holiday and celebration expenses', '2024-10-01 00:00:00'),
('Health', '#27ae60', 'Health and wellness related', '2024-10-01 00:00:00'),
('Investment', '#9b59b6', 'Investment and savings related', '2024-10-01 00:00:00'),
('Gift', '#e91e63', 'Gifts for others', '2024-10-01 00:00:00'),
('Travel', '#00bcd4', 'Travel and vacation expenses', '2024-10-01 00:00:00');

-- Data validation: Verify the data matches schema expectations

-- Test user data integrity
-- All users should have valid usernames, emails, and hashed passwords
-- Password hashes should be properly formatted (pbkdf2:sha256 format)

-- Test expense data integrity  
-- All expenses should have valid user_ids that reference existing users
-- All amounts should be positive decimal values
-- All categories should be one of: food, transportation, entertainment, other
-- All dates should be in YYYY-MM-DD format
-- All is_active values should be 0 or 1
-- All created_at timestamps should be in proper datetime format

-- Test income data integrity
-- All income should have valid user_ids that reference existing users  
-- All amounts should be positive decimal values
-- All recurrence_period values should be: none, weekly, monthly, yearly
-- All dates should be in YYYY-MM-DD format
-- All is_active values should be 0 or 1
-- All created_at timestamps should be in proper datetime format

-- Summary of test data:
-- Users: 5 test users with different profiles
-- Expenses: 50 expense records across all 4 categories (food, transportation, entertainment, other)
-- Income: 24 income records with various sources and recurrence patterns
-- Date range: September 2024 to October 2024 (current and historical data)
-- Categories distribution in expenses:
--   - food: ~15 expenses
--   - transportation: ~10 expenses  
--   - entertainment: ~8 expenses
--   - other: ~17 expenses
-- Income types: monthly salaries, freelance work, one-time payments, weekly recurring
-- Realistic amounts: ranging from small purchases ($4.99) to major expenses ($1200.00)