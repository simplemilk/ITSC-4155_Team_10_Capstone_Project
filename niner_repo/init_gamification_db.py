#!/usr/bin/env python3
"""
Initialize gamification database tables
"""
import os
import sqlite3

def get_db_path():
    """Get database path in instance folder"""
    base = os.path.dirname(os.path.abspath(__file__))
    instance_dir = os.path.join(base, 'instance')
    os.makedirs(instance_dir, exist_ok=True)
    return os.path.join(instance_dir, 'niner_finance.sqlite')

def init_gamification_db():
    """Initialize gamification tables"""
    db_path = get_db_path()
    print(f"\n🎮 Initializing gamification tables...")
    print(f"Database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. User game progress table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_game_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                total_points INTEGER DEFAULT 0,
                current_level INTEGER DEFAULT 1,
                experience_points INTEGER DEFAULT 0,
                streak_days INTEGER DEFAULT 0,
                longest_streak INTEGER DEFAULT 0,
                last_activity_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        
        # 2. Levels table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS levels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level_number INTEGER UNIQUE NOT NULL,
                level_name TEXT NOT NULL,
                experience_required INTEGER NOT NULL,
                points_multiplier REAL DEFAULT 1.0,
                badge_icon TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert default levels
        levels_data = [
            (1, 'Beginner', 0, 1.0, 'fa-seedling'),
            (2, 'Novice', 100, 1.1, 'fa-leaf'),
            (3, 'Learner', 250, 1.2, 'fa-book'),
            (4, 'Saver', 500, 1.3, 'fa-piggy-bank'),
            (5, 'Budgeter', 1000, 1.4, 'fa-calculator'),
            (6, 'Investor', 2000, 1.5, 'fa-chart-line'),
            (7, 'Planner', 4000, 1.6, 'fa-tasks'),
            (8, 'Expert', 7500, 1.7, 'fa-user-graduate'),
            (9, 'Master', 12000, 1.8, 'fa-crown'),
            (10, 'Financial Wizard', 20000, 2.0, 'fa-hat-wizard'),
        ]
        
        cursor.executemany('''
            INSERT OR IGNORE INTO levels (level_number, level_name, experience_required, points_multiplier, badge_icon)
            VALUES (?, ?, ?, ?, ?)
        ''', levels_data)
        
        # 3. Milestones table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS milestones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                category TEXT NOT NULL,
                criteria_type TEXT NOT NULL,
                criteria_value INTEGER NOT NULL,
                points_reward INTEGER DEFAULT 0,
                badge_icon TEXT,
                badge_color TEXT,
                tier TEXT DEFAULT 'bronze',
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert default milestones
        milestones_data = [
            # Transaction milestones
            ('First Transaction', 'Log your first transaction', 'transaction', 'count', 1, 10, 'fa-receipt', '#3498db', 'bronze', 1),
            ('Getting Started', 'Log 5 transactions', 'transaction', 'count', 5, 25, 'fa-chart-line', '#2ecc71', 'bronze', 1),
            ('Transaction Pro', 'Log 25 transactions', 'transaction', 'count', 25, 100, 'fa-tasks', '#f39c12', 'silver', 1),
            ('Transaction Master', 'Log 100 transactions', 'transaction', 'count', 100, 500, 'fa-trophy', '#e67e22', 'gold', 1),
            
            # Budget milestones
            ('Budget Creator', 'Create your first budget', 'budget', 'count', 1, 50, 'fa-calculator', '#9b59b6', 'bronze', 1),
            ('Budget Planner', 'Create 5 budgets', 'budget', 'count', 5, 150, 'fa-clipboard-list', '#8e44ad', 'silver', 1),
            
            # Savings milestones
            ('Savings Started', 'Save $100', 'savings', 'amount', 100, 100, 'fa-coins', '#27ae60', 'bronze', 1),
            ('Savings Builder', 'Save $500', 'savings', 'amount', 500, 250, 'fa-piggy-bank', '#16a085', 'silver', 1),
            ('Savings Expert', 'Save $1000', 'savings', 'amount', 1000, 500, 'fa-money-bill-wave', '#2ecc71', 'gold', 1),
            
            # Streak milestones
            ('Week Warrior', 'Maintain a 7-day streak', 'streak', 'days', 7, 75, 'fa-fire', '#e74c3c', 'bronze', 1),
            ('Month Master', 'Maintain a 30-day streak', 'streak', 'days', 30, 200, 'fa-calendar-check', '#c0392b', 'gold', 1),
            
            # Goal milestones
            ('Goal Setter', 'Create your first financial goal', 'goal', 'count', 1, 75, 'fa-bullseye', '#e67e22', 'bronze', 1),
            ('Goal Achiever', 'Complete a financial goal', 'goal', 'completed', 1, 250, 'fa-trophy', '#f39c12', 'gold', 1),
        ]
        
        cursor.executemany('''
            INSERT OR IGNORE INTO milestones (name, description, category, criteria_type, criteria_value, 
                                             points_reward, badge_icon, badge_color, tier, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', milestones_data)
        
        # 4. User achievements table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                milestone_id INTEGER NOT NULL,
                progress_value INTEGER DEFAULT 0,
                is_completed INTEGER DEFAULT 0,
                achieved_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (milestone_id) REFERENCES milestones (id) ON DELETE CASCADE,
                UNIQUE(user_id, milestone_id)
            )
        ''')
        
        # 5. Badges table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS badges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                icon TEXT,
                color TEXT,
                rarity TEXT DEFAULT 'common',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert default badges
        badges_data = [
            ('Welcome Niner', 'Welcome to Niner Finance!', 'fa-handshake', '#00703C', 'common'),
            ('Budget Master', 'Mastered budget planning', 'fa-crown', '#B3A369', 'rare'),
            ('Savings Star', 'Excellent at saving money', 'fa-star', '#FFD700', 'rare'),
            ('Transaction Pro', 'Expert at tracking transactions', 'fa-receipt', '#3498db', 'uncommon'),
            ('Financial Wizard', 'Reached level 10', 'fa-hat-wizard', '#9b59b6', 'legendary'),
        ]
        
        cursor.executemany('''
            INSERT OR IGNORE INTO badges (name, description, icon, color, rarity)
            VALUES (?, ?, ?, ?, ?)
        ''', badges_data)
        
        # 6. User badges table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_badges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                badge_id INTEGER NOT NULL,
                earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (badge_id) REFERENCES badges (id) ON DELETE CASCADE,
                UNIQUE(user_id, badge_id)
            )
        ''')
        
        # 7. Game activities table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                activity_type TEXT NOT NULL,
                points_earned INTEGER DEFAULT 0,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        
        # 8. User streaks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_streaks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                current_streak INTEGER DEFAULT 0,
                longest_streak INTEGER DEFAULT 0,
                last_activity_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_achievements_user_id ON user_achievements(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_achievements_completed ON user_achievements(is_completed)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_badges_user_id ON user_badges(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_game_activities_user_id ON game_activities(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_game_progress_user_id ON user_game_progress(user_id)')
        
        conn.commit()
        conn.close()
        
        print("✓ Gamification tables created successfully")
        print(f"  - user_game_progress")
        print(f"  - levels ({len(levels_data)} levels)")
        print(f"  - milestones ({len(milestones_data)} milestones)")
        print(f"  - user_achievements")
        print(f"  - badges ({len(badges_data)} badges)")
        print(f"  - user_badges")
        print(f"  - game_activities")
        print(f"  - user_streaks")
        
        return True
        
    except Exception as e:
        print(f"❌ Error initializing gamification: {e}")
        import traceback
        traceback.print_exc()
        return False

def remove_milestone_duplicates(db_path):
    conn = sqlite3.connect(db_path)
    conn.execute("""
        DELETE FROM milestones
        WHERE rowid NOT IN (
            SELECT MIN(rowid)
            FROM milestones
            GROUP BY name, category
        );
    """)
    conn.commit()
    conn.close()

if __name__ == '__main__':
    import sys
    success = init_gamification_db()
    remove_milestone_duplicates('instance/niner_finance.sqlite')
    sys.exit(0 if success else 1)