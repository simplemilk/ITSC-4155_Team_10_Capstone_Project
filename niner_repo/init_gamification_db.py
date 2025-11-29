import sqlite3
import os

def init_gamification_db():
    """Initialize the gamification database tables"""
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'niner_finance.sqlite')
    
    print(f"📂 Initializing gamification database at: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Execute the schema
    print("📝 Creating gamification tables...")
    
    schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gamification_schema.sql')
    
    if os.path.exists(schema_path):
        with open(schema_path, 'r') as f:
            conn.executescript(f.read())
    else:
        # If schema file doesn't exist, create tables directly
        print("Schema file not found, creating tables directly...")
        
        # User Progress
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_game_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                total_points INTEGER DEFAULT 0,
                current_level INTEGER DEFAULT 1,
                experience_points INTEGER DEFAULT 0,
                streak_days INTEGER DEFAULT 0,
                last_activity_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user (id) ON DELETE CASCADE
            )
        ''')
        
        # Milestones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS milestones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                criteria_type TEXT NOT NULL,
                criteria_value REAL NOT NULL,
                points_reward INTEGER NOT NULL,
                badge_icon TEXT,
                badge_color TEXT,
                tier TEXT DEFAULT 'bronze',
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User Achievements
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                milestone_id INTEGER NOT NULL,
                achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                progress_value REAL DEFAULT 0,
                is_completed INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES user (id) ON DELETE CASCADE,
                FOREIGN KEY (milestone_id) REFERENCES milestones (id) ON DELETE CASCADE,
                UNIQUE(user_id, milestone_id)
            )
        ''')
        
        # Levels
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS levels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level_number INTEGER NOT NULL UNIQUE,
                level_name TEXT NOT NULL,
                experience_required INTEGER NOT NULL,
                points_multiplier REAL DEFAULT 1.0,
                badge_icon TEXT,
                perks TEXT
            )
        ''')
        
        # Activity Log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                activity_type TEXT NOT NULL,
                points_earned INTEGER NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user (id) ON DELETE CASCADE
            )
        ''')
        
        # Streaks
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_streaks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                current_streak INTEGER DEFAULT 0,
                longest_streak INTEGER DEFAULT 0,
                last_activity_date TEXT,
                streak_type TEXT DEFAULT 'daily',
                FOREIGN KEY (user_id) REFERENCES user (id) ON DELETE CASCADE
            )
        ''')
        
        # Badges
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS badges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                icon TEXT NOT NULL,
                color TEXT DEFAULT '#FFD700',
                rarity TEXT DEFAULT 'common',
                category TEXT
            )
        ''')
        
        # User Badges
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_badges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                badge_id INTEGER NOT NULL,
                earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user (id) ON DELETE CASCADE,
                FOREIGN KEY (badge_id) REFERENCES badges (id) ON DELETE CASCADE,
                UNIQUE(user_id, badge_id)
            )
        ''')
        
        # Insert default levels
        levels_data = [
            (1, 'Financial Rookie', 0, 1.0, 'fa-seedling'),
            (2, 'Money Manager', 100, 1.1, 'fa-chart-line'),
            (3, 'Budget Master', 250, 1.2, 'fa-coins'),
            (4, 'Savings Champion', 500, 1.3, 'fa-piggy-bank'),
            (5, 'Investment Guru', 1000, 1.5, 'fa-gem'),
            (6, 'Financial Wizard', 2000, 1.7, 'fa-crown'),
            (7, 'Wealth Builder', 3500, 2.0, 'fa-trophy'),
            (8, 'Money Mogul', 5000, 2.5, 'fa-star'),
            (9, 'Finance Legend', 7500, 3.0, 'fa-medal'),
            (10, 'Ultimate Niner', 10000, 4.0, 'fa-fire')
        ]
        
        cursor.executemany('''
            INSERT OR IGNORE INTO levels (level_number, level_name, experience_required, points_multiplier, badge_icon)
            VALUES (?, ?, ?, ?, ?)
        ''', levels_data)
        
        # Insert default milestones
        milestones_data = [
            ('First Budget', 'Create your first budget', 'budget', 'count', 1, 50, 'fa-file-invoice-dollar', '#3498db', 'bronze'),
            ('Budget Veteran', 'Create 5 budgets', 'budget', 'count', 5, 200, 'fa-file-invoice-dollar', '#95a5a6', 'silver'),
            ('Budget Master', 'Create 10 budgets', 'budget', 'count', 10, 500, 'fa-file-invoice-dollar', '#f39c12', 'gold'),
            ('Savings Starter', 'Save your first $100', 'savings', 'amount', 100, 100, 'fa-piggy-bank', '#3498db', 'bronze'),
            ('Savings Pro', 'Save $1,000', 'savings', 'amount', 1000, 300, 'fa-piggy-bank', '#95a5a6', 'silver'),
            ('First Investment', 'Make your first investment', 'investment', 'count', 1, 150, 'fa-chart-line', '#3498db', 'bronze'),
            ('Portfolio Builder', 'Have 5 different investments', 'investment', 'count', 5, 400, 'fa-chart-line', '#95a5a6', 'silver'),
            ('Transaction Tracker', 'Log 10 transactions', 'transaction', 'count', 10, 50, 'fa-exchange-alt', '#3498db', 'bronze'),
            ('Week Warrior', 'Log activity for 7 days straight', 'streak', 'streak', 7, 100, 'fa-fire', '#e74c3c', 'bronze'),
            ('Goal Setter', 'Create your first financial goal', 'goal', 'count', 1, 75, 'fa-bullseye', '#3498db', 'bronze'),
            ('Goal Achiever', 'Complete your first financial goal', 'goal', 'completion', 1, 250, 'fa-check-circle', '#27ae60', 'silver')
        ]
        
        cursor.executemany('''
            INSERT OR IGNORE INTO milestones (name, description, category, criteria_type, criteria_value, points_reward, badge_icon, badge_color, tier)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', milestones_data)
        
        # Insert default badges
        badges_data = [
            ('Welcome Niner', 'Join Niner Finance', 'fa-handshake', '#3498db', 'common', 'onboarding'),
            ('First Steps', 'Complete your profile', 'fa-user-check', '#27ae60', 'common', 'profile'),
            ('Budget Boss', 'Master of budgeting', 'fa-crown', '#f39c12', 'rare', 'budget'),
            ('Savings Star', 'Exceptional saver', 'fa-star', '#FFD700', 'epic', 'savings'),
            ('Investment Icon', 'Investment expert', 'fa-gem', '#9b59b6', 'epic', 'investment'),
            ('Streak Legend', 'Maintained longest streak', 'fa-fire', '#e74c3c', 'legendary', 'streak'),
            ('Financial Wizard', 'Reached level 10', 'fa-hat-wizard', '#8e44ad', 'legendary', 'level')
        ]
        
        cursor.executemany('''
            INSERT OR IGNORE INTO badges (name, description, icon, color, rarity, category)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', badges_data)
    
    conn.commit()
    
    # Verify tables were created
    tables = cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND (name LIKE '%game%' OR name LIKE '%milestone%' OR name LIKE '%badge%' OR name LIKE '%level%')"
    ).fetchall()
    
    conn.close()
    
    if len(tables) >= 8:
        print(f"✓ Gamification database initialized successfully!")
        print(f"  Created tables: {', '.join([t[0] for t in tables])}")
        return True
    else:
        print(f"❌ Failed to create gamification tables")
        print(f"  Only created: {', '.join([t[0] for t in tables])}")
        return False

if __name__ == '__main__':
    init_gamification_db()