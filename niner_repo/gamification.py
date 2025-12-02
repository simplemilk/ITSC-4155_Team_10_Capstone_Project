from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, g
from db import get_db
from auth import login_required
from datetime import datetime, timedelta
import json
import sqlite3

bp = Blueprint('gamification', __name__, url_prefix='/game')

# ============================================================================
# DASHBOARD & OVERVIEW
# ============================================================================

@bp.route('/')
@login_required
def dashboard():
    """Main gamification dashboard"""
    db = get_db()
    
    # Get or create user progress
    progress = get_user_progress(g.user['id'])
    
    # Get user achievements
    achievements = db.execute(
        '''SELECT ua.*, m.name, m.description, m.badge_icon, m.badge_color, 
                  m.points_reward, m.tier, m.criteria_value
           FROM user_achievements ua
           JOIN milestones m ON ua.milestone_id = m.id
           WHERE ua.user_id = ? AND ua.is_completed = 1
           ORDER BY ua.achieved_at DESC''',
        (g.user['id'],)
    ).fetchall()
    
    # Get in-progress milestones
    in_progress = db.execute(
        '''SELECT ua.*, m.name, m.description, m.badge_icon, m.badge_color,
                  m.criteria_value, m.criteria_type
           FROM user_achievements ua
           JOIN milestones m ON ua.milestone_id = m.id
           WHERE ua.user_id = ? AND ua.is_completed = 0
           ORDER BY (ua.progress_value / m.criteria_value) DESC
           LIMIT 5''',
        (g.user['id'],)
    ).fetchall()
    
    # Get recent activities
    recent_activities = db.execute(
        '''SELECT * FROM game_activities
           WHERE user_id = ?
           ORDER BY created_at DESC
           LIMIT 10''',
        (g.user['id'],)
    ).fetchall()
    
    # Get user badges
    badges = db.execute(
        '''SELECT ub.*, b.name, b.description, b.icon, b.color, b.rarity
           FROM user_badges ub
           JOIN badges b ON ub.badge_id = b.id
           WHERE ub.user_id = ?
           ORDER BY ub.earned_at DESC''',
        (g.user['id'],)
    ).fetchall()
    
    # Get current level info
    current_level = db.execute(
        'SELECT * FROM levels WHERE level_number = ?',
        (progress['current_level'],)
    ).fetchone()
    
    # Get next level info
    next_level = db.execute(
        'SELECT * FROM levels WHERE level_number = ?',
        (progress['current_level'] + 1,)
    ).fetchone()
    
    # Get leaderboard position
    leaderboard_position = get_leaderboard_position(g.user['id'])
    
    return render_template(
        'game/dashboard.html',
        progress=progress,
        achievements=achievements,
        in_progress=in_progress,
        recent_activities=recent_activities,
        badges=badges,
        current_level=current_level,
        next_level=next_level,
        leaderboard_position=leaderboard_position
    )

@bp.route('/milestones')
@login_required
def milestones():
    """View all available milestones"""
    db = get_db()
    
    # Get all milestones with user progress
    all_milestones = db.execute(
        '''SELECT m.*, 
                  COALESCE(ua.progress_value, 0) as progress_value,
                  COALESCE(ua.is_completed, 0) as is_completed,
                  ua.achieved_at
           FROM milestones m
           LEFT JOIN user_achievements ua ON m.id = ua.milestone_id AND ua.user_id = ?
           WHERE m.is_active = 1
           ORDER BY m.category, m.criteria_value''',
        (g.user['id'],)
    ).fetchall()
    
    # Group by category
    milestones_by_category = {}
    for milestone in all_milestones:
        category = milestone['category']
        if category not in milestones_by_category:
            milestones_by_category[category] = []
        milestones_by_category[category].append(milestone)
    
    return render_template(
        'game/milestones.html',
        milestones_by_category=milestones_by_category
    )

@bp.route('/leaderboard')
@login_required
def leaderboard():
    """View leaderboard"""
    db = get_db()
    
    # Get top users by points
    top_users = db.execute(
        '''SELECT u.id, u.username, ugp.total_points, ugp.current_level,
                  ugp.streak_days, COUNT(ua.id) as achievements_count
           FROM user u
           JOIN user_game_progress ugp ON u.id = ugp.user_id
           LEFT JOIN user_achievements ua ON u.id = ua.user_id AND ua.is_completed = 1
           GROUP BY u.id
           ORDER BY ugp.total_points DESC
           LIMIT 100''',
    ).fetchall()
    
    # Get current user's rank
    user_rank = get_leaderboard_position(g.user['id'])
    
    return render_template(
        'game/leaderboard.html',
        top_users=top_users,
        user_rank=user_rank
    )

# ============================================================================
# PROGRESS TRACKING & POINTS
# ============================================================================

def get_user_progress(user_id):
    """Get or create user game progress"""
    db = get_db()
    
    progress = db.execute(
        'SELECT * FROM user_game_progress WHERE user_id = ?',
        (user_id,)
    ).fetchone()
    
    if not progress:
        # Create initial progress
        db.execute(
            '''INSERT INTO user_game_progress (user_id, total_points, current_level, experience_points)
               VALUES (?, 0, 1, 0)''',
            (user_id,)
        )
        db.commit()
        
        progress = db.execute(
            'SELECT * FROM user_game_progress WHERE user_id = ?',
            (user_id,)
        ).fetchone()
        
        # Award welcome badge
        award_badge(user_id, 'Welcome Niner')
    
    return progress

def complete_milestone(user_id, milestone_id):
    """Mark milestone as completed and award points"""
    db = get_db()
    
    # Check if already completed
    achievement = db.execute(
        'SELECT * FROM user_achievements WHERE user_id = ? AND milestone_id = ?',
        (user_id, milestone_id)
    ).fetchone()
    
    if achievement and achievement['is_completed']:
        return  # Already completed - DON'T flash again
    
    # Get milestone details
    milestone = db.execute(
        'SELECT * FROM milestones WHERE id = ?',
        (milestone_id,)
    ).fetchone()
    
    if not milestone:
        return
    
    # Mark as completed
    if achievement:
        db.execute(
            '''UPDATE user_achievements 
               SET is_completed = 1, achieved_at = CURRENT_TIMESTAMP
               WHERE user_id = ? AND milestone_id = ?''',
            (user_id, milestone_id)
        )
    else:
        db.execute(
            '''INSERT INTO user_achievements (user_id, milestone_id, progress_value, is_completed, achieved_at)
               VALUES (?, ?, ?, 1, CURRENT_TIMESTAMP)''',
            (user_id, milestone_id, milestone['criteria_value'])
        )
    db.commit()
    
    # Award points
    points_awarded = award_points(
        user_id,
        milestone['points_reward'],
        f'milestone_{milestone["category"]}',
        f'Completed: {milestone["name"]}'
    )
    
    # ONLY flash if we just completed it
    achievement_data = {
        'type': 'achievement',
        'name': milestone['name'],
        'description': milestone['description'],
        'points': points_awarded,
        'icon': milestone['badge_icon'],
        'color': milestone['badge_color'],
        'tier': milestone['tier']
    }
    
    flash(json.dumps(achievement_data), 'achievement')
    
    # Award tier-specific badges
    if milestone['tier'] == 'platinum':
        award_badge(user_id, f'{milestone["category"].title()} Master')

def award_badge(user_id, badge_name):
    """Award a badge to user"""
    db = get_db()
    
    # Get badge
    badge = db.execute(
        'SELECT * FROM badges WHERE name = ?',
        (badge_name,)
    ).fetchone()
    
    if not badge:
        return
    
    # Check if already awarded
    existing = db.execute(
        'SELECT * FROM user_badges WHERE user_id = ? AND badge_id = ?',
        (user_id, badge['id'])
    ).fetchone()
    
    if existing:
        return
    
    # Award badge
    db.execute(
        'INSERT INTO user_badges (user_id, badge_id) VALUES (?, ?)',
        (user_id, badge['id'])
    )
    db.commit()
    
    # Create badge data for popup
    badge_data = {
        'type': 'badge',
        'name': badge['name'],
        'description': badge['description'],
        'icon': badge['icon'],
        'color': badge['color'],
        'rarity': badge['rarity']
    }
    
    flash(json.dumps(badge_data), 'badge')

def award_points(user_id, points, activity_type, description):
    """Award points to user and check for level up"""
    db = get_db()
    
    # Get current progress
    progress = get_user_progress(user_id)
    
    # Get current level multiplier
    level = db.execute(
        'SELECT points_multiplier FROM levels WHERE level_number = ?',
        (progress['current_level'],)
    ).fetchone()
    
    multiplier = level['points_multiplier'] if level else 1.0
    actual_points = int(points * multiplier)
    
    # Update points and experience
    new_total = progress['total_points'] + actual_points
    new_exp = progress['experience_points'] + actual_points
    
    # Check for level up
    next_level = db.execute(
        '''SELECT * FROM levels 
           WHERE level_number = ? AND experience_required <= ?
           ORDER BY level_number DESC LIMIT 1''',
        (progress['current_level'] + 1, new_exp)
    ).fetchone()
    
    new_level = progress['current_level']
    if next_level:
        new_level = next_level['level_number']
        
        # Create level up data for popup
        level_data = {
            'type': 'level_up',
            'level': new_level,
            'level_name': next_level['level_name'],
            'icon': next_level['badge_icon'],
            'multiplier': next_level['points_multiplier']
        }
        flash(json.dumps(level_data), 'level_up')
        
        # Award level-up badge if applicable
        if new_level == 10:
            award_badge(user_id, 'Financial Wizard')
    
    # Update progress
    db.execute(
        '''UPDATE user_game_progress 
           SET total_points = ?, experience_points = ?, current_level = ?, 
               updated_at = CURRENT_TIMESTAMP
           WHERE user_id = ?''',
        (new_total, new_exp, new_level, user_id)
    )
    
    # Log activity
    db.execute(
        '''INSERT INTO game_activities (user_id, activity_type, points_earned, description)
           VALUES (?, ?, ?, ?)''',
        (user_id, activity_type, actual_points, description)
    )
    
    db.commit()
    
    return actual_points

def check_milestone_progress(user_id, milestone_category, current_value):
    """Check if user has achieved any milestones"""
    db = get_db()
    
    # Get relevant milestones that are NOT completed yet
    milestones = db.execute(
        '''SELECT m.* FROM milestones m
           LEFT JOIN user_achievements ua ON m.id = ua.milestone_id AND ua.user_id = ?
           WHERE m.category = ? AND m.is_active = 1
           AND (ua.is_completed = 0 OR ua.id IS NULL)
           ORDER BY m.criteria_value ASC''',
        (user_id, milestone_category)
    ).fetchall()
    
    for milestone in milestones:
        # Get or create achievement record
        achievement = db.execute(
            'SELECT * FROM user_achievements WHERE user_id = ? AND milestone_id = ?',
            (user_id, milestone['id'])
        ).fetchone()
        
        if not achievement:
            db.execute(
                '''INSERT INTO user_achievements (user_id, milestone_id, progress_value)
                   VALUES (?, ?, ?)''',
                (user_id, milestone['id'], current_value)
            )
            db.commit()
        elif not achievement['is_completed']:  # Only update if not completed
            # Update progress
            db.execute(
                'UPDATE user_achievements SET progress_value = ? WHERE id = ?',
                (current_value, achievement['id'])
            )
            db.commit()
        
        # Check if milestone is achieved (and not already completed)
        if current_value >= milestone['criteria_value']:
            if not achievement or not achievement['is_completed']:
                complete_milestone(user_id, milestone['id'])
                break  # Only complete ONE milestone per check to avoid spam

def update_streak(user_id):
    """Update user's activity streak"""
    db = get_db()
    today = datetime.now().date().isoformat()
    
    # Get or create streak record
    streak = db.execute(
        'SELECT * FROM user_streaks WHERE user_id = ?',
        (user_id,)
    ).fetchone()
    
    if not streak:
        db.execute(
            '''INSERT INTO user_streaks (user_id, current_streak, longest_streak, last_activity_date)
               VALUES (?, 1, 1, ?)''',
            (user_id, today)
        )
        db.commit()
        
        # Also update user_game_progress
        db.execute(
            'UPDATE user_game_progress SET streak_days = 1, last_activity_date = ? WHERE user_id = ?',
            (today, user_id)
        )
        db.commit()
        return 1
    
    last_date = datetime.fromisoformat(streak['last_activity_date']).date() if streak['last_activity_date'] else None
    yesterday = (datetime.now() - timedelta(days=1)).date()
    
    if last_date == datetime.now().date():
        # Already logged today
        return streak['current_streak']
    elif last_date == yesterday:
        # Continuing streak
        new_streak = streak['current_streak'] + 1
        new_longest = max(new_streak, streak['longest_streak'])
        
        db.execute(
            '''UPDATE user_streaks 
               SET current_streak = ?, longest_streak = ?, last_activity_date = ?
               WHERE user_id = ?''',
            (new_streak, new_longest, today, user_id)
        )
        
        # Update user_game_progress
        db.execute(
            'UPDATE user_game_progress SET streak_days = ?, last_activity_date = ? WHERE user_id = ?',
            (new_streak, today, user_id)
        )
        db.commit()
        
        # Check streak milestones
        check_milestone_progress(user_id, 'streak', new_streak)
        
        # Award points for continuing streak
        award_points(user_id, new_streak * 5, 'streak_continued', f'{new_streak} day streak!')
        
        return new_streak
    else:
        # Streak broken
        db.execute(
            '''UPDATE user_streaks 
               SET current_streak = 1, last_activity_date = ?
               WHERE user_id = ?''',
            (today, user_id)
        )
        
        # Update user_game_progress
        db.execute(
            'UPDATE user_game_progress SET streak_days = 1, last_activity_date = ? WHERE user_id = ?',
            (today, user_id)
        )
        db.commit()
        return 1

def get_leaderboard_position(user_id):
    """Get user's position on leaderboard"""
    db = get_db()
    
    position = db.execute(
        '''SELECT COUNT(*) + 1 as position
           FROM user_game_progress
           WHERE total_points > (
               SELECT total_points FROM user_game_progress WHERE user_id = ?
           )''',
        (user_id,)
    ).fetchone()
    
    return position['position'] if position else None

# ============================================================================
# ACTIVITY HOOKS (Called from other modules)
# ============================================================================

def on_budget_created(user_id):
    """Called when user creates a budget"""
    award_points(user_id, 50, 'budget_created', 'Created a new budget')
    
    # Count total budgets
    db = get_db()
    budget_count = db.execute(
        'SELECT COUNT(*) as count FROM budgets WHERE user_id = ?',
        (user_id,)
    ).fetchone()['count']
    
    check_milestone_progress(user_id, 'budget', budget_count)
    update_streak(user_id)

def on_transaction_added(user_id):
    """Called when user logs a transaction"""
    award_points(user_id, 10, 'transaction_added', 'Logged a transaction')
    
    # Count total transactions
    db = get_db()
    transaction_count = db.execute(
        'SELECT COUNT(*) as count FROM transactions WHERE user_id = ?',
        (user_id,)
    ).fetchone()['count']
    
    check_milestone_progress(user_id, 'transaction', transaction_count)
    update_streak(user_id)

def on_investment_added(user_id):
    """Called when user adds an investment"""
    award_points(user_id, 150, 'investment_added', 'Added an investment')
    
    # Count total investments
    db = get_db()
    investment_count = db.execute(
        'SELECT COUNT(*) as count FROM investments WHERE user_id = ?',
        (user_id,)
    ).fetchone()['count']
    
    check_milestone_progress(user_id, 'investment', investment_count)
    update_streak(user_id)

def on_goal_created(user_id):
    """Called when user creates a financial goal"""
    award_points(user_id, 75, 'goal_created', 'Created a financial goal')
    
    db = get_db()
    goal_count = db.execute(
        'SELECT COUNT(*) as count FROM financial_goals WHERE user_id = ?',
        (user_id,)
    ).fetchone()['count']
    
    check_milestone_progress(user_id, 'goal', goal_count)
    update_streak(user_id)

def on_goal_completed(user_id):
    """Called when user completes a financial goal"""
    award_points(user_id, 250, 'goal_completed', 'Completed a financial goal!')
    
    db = get_db()
    completed_goals = db.execute(
        '''SELECT COUNT(*) as count FROM financial_goals 
           WHERE user_id = ? AND current_amount >= target_amount''',
        (user_id,)
    ).fetchone()['count']
    
    check_milestone_progress(user_id, 'goal', completed_goals)

def on_savings_milestone(user_id, total_savings):
    """Called when user's savings reach a milestone"""
    check_milestone_progress(user_id, 'savings', total_savings)

# Export functions for use in other modules
__all__ = [
    'on_budget_created',
    'on_transaction_added',
    'on_investment_added',
    'on_goal_created',
    'on_goal_completed',
    'on_savings_milestone',
    'award_points',
    'award_badge',
    'update_streak'
]

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

# Call this after all milestone inserts
remove_milestone_duplicates('instance/niner_finance.sqlite')