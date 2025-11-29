import pytest
from datetime import datetime, timedelta
from db import get_db
from gamification import (
    get_user_progress,
    award_points,
    check_milestone_progress,
    complete_milestone,
    award_badge,
    update_streak,
    on_budget_created,
    on_transaction_added,
    on_investment_added,
    on_goal_created,
    on_goal_completed
)

# ============================================================================
# INITIALIZATION TESTS
# ============================================================================

def test_gamification_page_access(client, auth):
    """Test accessing the game dashboard"""
    auth.login()
    response = client.get('/game/')
    assert response.status_code == 200
    assert b'Game Dashboard' in response.data

def test_gamification_requires_login(client):
    """Test that gamification requires authentication"""
    response = client.get('/game/')
    assert response.status_code == 302
    assert b'login' in response.location.lower().encode()

def test_user_progress_initialization(client, auth, app):
    """Test that user progress is created on first access"""
    auth.login()
    
    with app.app_context():
        progress = get_user_progress(1)
        
        assert progress is not None
        assert progress['user_id'] == 1
        assert progress['total_points'] == 0
        assert progress['current_level'] == 1
        assert progress['experience_points'] == 0

# ============================================================================
# POINTS & LEVELS TESTS
# ============================================================================

def test_award_points(client, auth, app):
    """Test awarding points to user"""
    auth.login()
    
    with app.app_context():
        # Award points
        points = award_points(1, 100, 'test_activity', 'Test description')
        
        assert points > 0
        
        # Verify points were added
        progress = get_user_progress(1)
        assert progress['total_points'] >= 100

def test_level_up(client, auth, app):
    """Test that user levels up when reaching XP threshold"""
    auth.login()
    
    with app.app_context():
        # Award enough points to level up
        award_points(1, 200, 'test', 'Level up test')
        
        progress = get_user_progress(1)
        # Should be level 2 or higher after 200 XP
        assert progress['current_level'] >= 2

def test_points_multiplier(client, auth, app):
    """Test that points are multiplied by level"""
    auth.login()
    
    with app.app_context():
        db = get_db()
        
        # Set user to level 5 (1.5x multiplier)
        db.execute(
            'UPDATE user_game_progress SET current_level = 5 WHERE user_id = ?',
            (1,)
        )
        db.commit()
        
        # Award 100 points
        points = award_points(1, 100, 'test', 'Multiplier test')
        
        # Should get 150 points (100 * 1.5)
        assert points == 150

# ============================================================================
# MILESTONES TESTS
# ============================================================================

def test_milestone_progress_tracking(client, auth, app):
    """Test that milestone progress is tracked correctly"""
    auth.login()
    
    with app.app_context():
        # Track progress for budget milestone
        check_milestone_progress(1, 'budget', 1)
        
        db = get_db()
        achievement = db.execute(
            '''SELECT ua.* FROM user_achievements ua
               JOIN milestones m ON ua.milestone_id = m.id
               WHERE ua.user_id = ? AND m.name = ?''',
            (1, 'First Budget')
        ).fetchone()
        
        assert achievement is not None
        assert achievement['progress_value'] == 1

def test_milestone_completion(client, auth, app):
    """Test completing a milestone"""
    auth.login()
    
    with app.app_context():
        db = get_db()
        
        # Get "First Budget" milestone
        milestone = db.execute(
            "SELECT id FROM milestones WHERE name = 'First Budget'"
        ).fetchone()
        
        # Complete it
        complete_milestone(1, milestone['id'])
        
        # Verify completion
        achievement = db.execute(
            'SELECT * FROM user_achievements WHERE user_id = ? AND milestone_id = ?',
            (1, milestone['id'])
        ).fetchone()
        
        assert achievement['is_completed'] == 1
        assert achievement['achieved_at'] is not None

def test_milestone_points_awarded(client, auth, app):
    """Test that points are awarded when completing milestone"""
    auth.login()
    
    with app.app_context():
        db = get_db()
        
        # Get initial points
        initial_progress = get_user_progress(1)
        initial_points = initial_progress['total_points']
        
        # Complete a milestone
        milestone = db.execute(
            "SELECT id FROM milestones WHERE name = 'First Budget'"
        ).fetchone()
        
        complete_milestone(1, milestone['id'])
        
        # Check points increased
        final_progress = get_user_progress(1)
        assert final_progress['total_points'] > initial_points

def test_view_milestones_page(client, auth):
    """Test viewing all milestones"""
    auth.login()
    
    response = client.get('/game/milestones')
    assert response.status_code == 200
    assert b'Milestones' in response.data
    assert b'First Budget' in response.data

# ============================================================================
# BADGES TESTS
# ============================================================================

def test_award_badge(client, auth, app):
    """Test awarding a badge to user"""
    auth.login()
    
    with app.app_context():
        award_badge(1, 'Welcome Niner')
        
        db = get_db()
        badge = db.execute(
            '''SELECT ub.* FROM user_badges ub
               JOIN badges b ON ub.badge_id = b.id
               WHERE ub.user_id = ? AND b.name = ?''',
            (1, 'Welcome Niner')
        ).fetchone()
        
        assert badge is not None

def test_duplicate_badge_prevention(client, auth, app):
    """Test that same badge can't be awarded twice"""
    auth.login()
    
    with app.app_context():
        db = get_db()
        
        # Award badge twice
        award_badge(1, 'Welcome Niner')
        award_badge(1, 'Welcome Niner')
        
        # Check only one entry exists
        count = db.execute(
            '''SELECT COUNT(*) as count FROM user_badges ub
               JOIN badges b ON ub.badge_id = b.id
               WHERE ub.user_id = ? AND b.name = ?''',
            (1, 'Welcome Niner')
        ).fetchone()['count']
        
        assert count == 1

# ============================================================================
# STREAK TESTS
# ============================================================================

def test_streak_initialization(client, auth, app):
    """Test that streak is initialized on first activity"""
    auth.login()
    
    with app.app_context():
        streak = update_streak(1)
        
        assert streak == 1

def test_streak_continuation(client, auth, app):
    """Test that streak continues when logging activity daily"""
    auth.login()
    
    with app.app_context():
        db = get_db()
        
        # Set last activity to yesterday
        yesterday = (datetime.now() - timedelta(days=1)).date().isoformat()
        db.execute(
            '''INSERT OR REPLACE INTO user_streaks 
               (user_id, current_streak, longest_streak, last_activity_date)
               VALUES (?, 5, 5, ?)''',
            (1, yesterday)
        )
        db.commit()
        
        # Update streak today
        streak = update_streak(1)
        
        # Should be 6 now
        assert streak == 6

def test_streak_broken(client, auth, app):
    """Test that streak resets when missing a day"""
    auth.login()
    
    with app.app_context():
        db = get_db()
        
        # Set last activity to 3 days ago
        three_days_ago = (datetime.now() - timedelta(days=3)).date().isoformat()
        db.execute(
            '''INSERT OR REPLACE INTO user_streaks 
               (user_id, current_streak, longest_streak, last_activity_date)
               VALUES (?, 10, 10, ?)''',
            (1, three_days_ago)
        )
        db.commit()
        
        # Update streak today
        streak = update_streak(1)
        
        # Should reset to 1
        assert streak == 1
        
        # But longest streak should still be 10
        streak_record = db.execute(
            'SELECT longest_streak FROM user_streaks WHERE user_id = ?',
            (1,)
        ).fetchone()
        assert streak_record['longest_streak'] == 10

# ============================================================================
# INTEGRATION TESTS WITH OTHER MODULES
# ============================================================================

def test_budget_creation_awards_points(client, auth, app):
    """Test that creating a budget awards points"""
    auth.login()
    
    with app.app_context():
        # Get initial points
        initial_progress = get_user_progress(1)
        initial_points = initial_progress['total_points']
        
        # Trigger budget creation event
        on_budget_created(1)
        
        # Check points increased
        final_progress = get_user_progress(1)
        assert final_progress['total_points'] > initial_points

def test_transaction_added_awards_points(client, auth, app):
    """Test that logging transaction awards points"""
    auth.login()
    
    with app.app_context():
        initial_progress = get_user_progress(1)
        initial_points = initial_progress['total_points']
        
        on_transaction_added(1)
        
        final_progress = get_user_progress(1)
        assert final_progress['total_points'] > initial_points

def test_investment_added_awards_points(client, auth, app):
    """Test that adding investment awards points"""
    auth.login()
    
    with app.app_context():
        initial_progress = get_user_progress(1)
        initial_points = initial_progress['total_points']
        
        on_investment_added(1)
        
        final_progress = get_user_progress(1)
        assert final_progress['total_points'] > initial_points

def test_goal_created_awards_points(client, auth, app):
    """Test that creating goal awards points"""
    auth.login()
    
    with app.app_context():
        initial_progress = get_user_progress(1)
        initial_points = initial_progress['total_points']
        
        on_goal_created(1)
        
        final_progress = get_user_progress(1)
        assert final_progress['total_points'] > initial_points

def test_goal_completed_awards_more_points(client, auth, app):
    """Test that completing goal awards bonus points"""
    auth.login()
    
    with app.app_context():
        initial_progress = get_user_progress(1)
        initial_points = initial_progress['total_points']
        
        on_goal_completed(1)
        
        final_progress = get_user_progress(1)
        # Goal completion should award more points than creation
        assert final_progress['total_points'] > initial_points + 200

def test_multiple_budgets_milestone(client, auth, app):
    """Test that creating multiple budgets progresses milestone"""
    auth.login()
    
    with app.app_context():
        # Create 5 budgets
        for i in range(5):
            on_budget_created(1)
        
        # Check if "Budget Veteran" milestone is completed
        db = get_db()
        achievement = db.execute(
            '''SELECT ua.* FROM user_achievements ua
               JOIN milestones m ON ua.milestone_id = m.id
               WHERE ua.user_id = ? AND m.name = ?''',
            (1, 'Budget Veteran')
        ).fetchone()
        
        assert achievement is not None
        assert achievement['is_completed'] == 1

# ============================================================================
# ACTIVITY LOG TESTS
# ============================================================================

def test_activity_logged(client, auth, app):
    """Test that activities are logged in game_activities table"""
    auth.login()
    
    with app.app_context():
        award_points(1, 50, 'test_activity', 'Test activity description')
        
        db = get_db()
        activity = db.execute(
            '''SELECT * FROM game_activities 
               WHERE user_id = ? AND activity_type = ?
               ORDER BY created_at DESC LIMIT 1''',
            (1, 'test_activity')
        ).fetchone()
        
        assert activity is not None
        assert activity['points_earned'] > 0
        assert activity['description'] == 'Test activity description'

# ============================================================================
# EDGE CASES & ERROR HANDLING
# ============================================================================

def test_gamification_handles_missing_user(app):
    """Test that gamification handles non-existent users gracefully"""
    with app.app_context():
        # This should not crash
        progress = get_user_progress(99999)
        assert progress is not None

def test_invalid_milestone_completion(app):
    """Test completing a non-existent milestone"""
    with app.app_context():
        # Should not crash
        complete_milestone(1, 99999)

def test_negative_points(app):
    """Test that negative points are handled"""
    with app.app_context():
        # Even with negative input, points should not decrease
        award_points(1, -100, 'test', 'Negative test')
        
        progress = get_user_progress(1)
        assert progress['total_points'] >= 0

# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

def test_bulk_point_awards(client, auth, app):
    """Test awarding points many times doesn't cause issues"""
    auth.login()
    
    with app.app_context():
        # Award points 100 times
        for i in range(100):
            award_points(1, 10, 'bulk_test', f'Bulk award {i}')
        
        progress = get_user_progress(1)
        # Should have at least 1000 points (100 * 10)
        assert progress['total_points'] >= 1000