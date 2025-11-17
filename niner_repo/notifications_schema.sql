-- Notifications Schema
-- Manages user notifications for overspending alerts and other financial events

-- Drop existing tables if they exist
DROP TABLE IF EXISTS notifications;
DROP TABLE IF EXISTS notification_settings;

-- Notifications table
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    type VARCHAR(50) NOT NULL CHECK (type IN ('overspending', 'budget_warning', 'goal_achieved', 'subscription_reminder', 'unusual_spending')),
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('info', 'warning', 'critical')),
    is_read BOOLEAN NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP,
    metadata TEXT,  -- JSON field for additional data (category, amount, etc.)
    FOREIGN KEY (user_id) REFERENCES user (id)
);

-- Create index for efficient queries
CREATE INDEX idx_notifications_user_unread ON notifications(user_id, is_read, created_at DESC);

-- Notification Settings table
CREATE TABLE notification_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    
    -- Notification type toggles
    enable_overspending BOOLEAN NOT NULL DEFAULT 1,
    enable_budget_warning BOOLEAN NOT NULL DEFAULT 1,
    enable_goal_achieved BOOLEAN NOT NULL DEFAULT 1,
    enable_subscription_reminder BOOLEAN NOT NULL DEFAULT 1,
    enable_unusual_spending BOOLEAN NOT NULL DEFAULT 1,
    
    -- Thresholds
    overspending_threshold INTEGER NOT NULL DEFAULT 100 CHECK (overspending_threshold >= 0 AND overspending_threshold <= 100),  -- percentage
    budget_warning_threshold INTEGER NOT NULL DEFAULT 90 CHECK (budget_warning_threshold >= 0 AND budget_warning_threshold <= 100),  -- percentage
    unusual_spending_multiplier DECIMAL(3,1) NOT NULL DEFAULT 2.0 CHECK (unusual_spending_multiplier >= 1.0),  -- times average
    
    -- Notification method preferences
    method_in_app BOOLEAN NOT NULL DEFAULT 1,
    method_email BOOLEAN NOT NULL DEFAULT 0,
    method_push BOOLEAN NOT NULL DEFAULT 0,
    
    -- Frequency controls
    daily_digest BOOLEAN NOT NULL DEFAULT 0,
    max_daily_notifications INTEGER NOT NULL DEFAULT 10 CHECK (max_daily_notifications >= 1 AND max_daily_notifications <= 50),
    
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES user (id)
);

-- Create trigger to create default settings for new users
CREATE TRIGGER create_default_notification_settings
AFTER INSERT ON user
BEGIN
    INSERT INTO notification_settings (user_id)
    VALUES (NEW.id);
END;

-- Create trigger to prevent duplicate notifications within short time window
CREATE TRIGGER prevent_duplicate_notifications
BEFORE INSERT ON notifications
WHEN EXISTS (
    SELECT 1 FROM notifications
    WHERE user_id = NEW.user_id
    AND type = NEW.type
    AND datetime(created_at) >= datetime('now', '-5 minutes')
)
BEGIN
    SELECT RAISE(IGNORE);
END;

-- Create view for unread notification counts by type
CREATE VIEW v_unread_notification_counts AS
SELECT 
    user_id,
    type,
    COUNT(*) as count
FROM notifications
WHERE is_read = 0
GROUP BY user_id, type;

-- Create view for notification summary
CREATE VIEW v_notification_summary AS
SELECT 
    n.user_id,
    COUNT(*) as total_notifications,
    SUM(CASE WHEN n.is_read = 0 THEN 1 ELSE 0 END) as unread_count,
    SUM(CASE WHEN n.severity = 'critical' AND n.is_read = 0 THEN 1 ELSE 0 END) as critical_unread,
    SUM(CASE WHEN n.severity = 'warning' AND n.is_read = 0 THEN 1 ELSE 0 END) as warning_unread,
    MAX(n.created_at) as last_notification_at
FROM notifications n
GROUP BY n.user_id;
