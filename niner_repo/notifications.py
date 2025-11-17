"""
Notification Engine Module
Handles detection of overspending, budget warnings, and other financial alerts
"""

from datetime import datetime, timedelta
from db import get_db
import json
from flask import g


class NotificationEngine:
    """Core notification engine for detecting and creating notifications"""
    
    # Notification type constants
    TYPE_OVERSPENDING = 'overspending'
    TYPE_BUDGET_WARNING = 'budget_warning'
    TYPE_GOAL_ACHIEVED = 'goal_achieved'
    TYPE_SUBSCRIPTION_REMINDER = 'subscription_reminder'
    TYPE_UNUSUAL_SPENDING = 'unusual_spending'
    
    # Severity levels
    SEVERITY_INFO = 'info'
    SEVERITY_WARNING = 'warning'
    SEVERITY_CRITICAL = 'critical'
    
    @staticmethod
    def get_user_settings(user_id):
        """Get notification settings for a user"""
        db = get_db()
        settings = db.execute(
            'SELECT * FROM notification_settings WHERE user_id = ?',
            (user_id,)
        ).fetchone()
        
        if not settings:
            # Create default settings if they don't exist
            db.execute(
                'INSERT INTO notification_settings (user_id) VALUES (?)',
                (user_id,)
            )
            db.commit()
            settings = db.execute(
                'SELECT * FROM notification_settings WHERE user_id = ?',
                (user_id,)
            ).fetchone()
        
        return dict(settings) if settings else None
    
    @staticmethod
    def create_notification(user_id, notification_type, title, message, severity, metadata=None):
        """Create a new notification"""
        db = get_db()
        settings = NotificationEngine.get_user_settings(user_id)
        
        # Check if this notification type is enabled
        enable_key = f'enable_{notification_type}'
        if not settings.get(enable_key, True):
            return None
        
        # Check daily notification limit
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_count = db.execute(
            '''SELECT COUNT(*) as count FROM notifications 
               WHERE user_id = ? AND created_at >= ?''',
            (user_id, today_start.isoformat())
        ).fetchone()
        
        if today_count and today_count['count'] >= settings.get('max_daily_notifications', 10):
            return None
        
        # Convert metadata to JSON string
        metadata_json = json.dumps(metadata) if metadata else None
        
        # Insert notification
        cursor = db.execute(
            '''INSERT INTO notifications 
               (user_id, type, title, message, severity, metadata)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (user_id, notification_type, title, message, severity, metadata_json)
        )
        db.commit()
        
        return cursor.lastrowid
    
    @staticmethod
    def check_overspending(user_id, category=None):
        """Check if user has exceeded budget and create notifications"""
        db = get_db()
        settings = NotificationEngine.get_user_settings(user_id)
        
        if not settings.get('enable_overspending', True):
            return []
        
        # Get current week dates
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        # Get current budget
        budget = db.execute(
            '''SELECT * FROM budgets 
               WHERE user_id = ? AND week_start_date = ?
               ORDER BY created_at DESC LIMIT 1''',
            (user_id, week_start.isoformat())
        ).fetchone()
        
        if not budget:
            return []
        
        notifications_created = []
        threshold = settings.get('overspending_threshold', 100)
        
        # Check overall budget
        total_budget = float(budget['total_amount'])
        total_spent_row = db.execute(
            '''SELECT COALESCE(SUM(amount), 0) as total
               FROM transactions 
               WHERE user_id = ? AND type = 'expense'
               AND date >= ? AND date <= ?''',
            (user_id, week_start.isoformat(), week_end.isoformat())
        ).fetchone()
        
        total_spent = float(total_spent_row['total']) if total_spent_row else 0.0
        spending_percentage = (total_spent / total_budget * 100) if total_budget > 0 else 0
        
        if spending_percentage >= threshold:
            notification_id = NotificationEngine.create_notification(
                user_id=user_id,
                notification_type=NotificationEngine.TYPE_OVERSPENDING,
                title='🚨 Budget Exceeded!',
                message=f'You have spent ${total_spent:.2f} of your ${total_budget:.2f} weekly budget ({spending_percentage:.0f}%).',
                severity=NotificationEngine.SEVERITY_CRITICAL,
                metadata={
                    'budget': total_budget,
                    'spent': total_spent,
                    'percentage': spending_percentage,
                    'category': 'overall'
                }
            )
            if notification_id:
                notifications_created.append(notification_id)
        
        # Check category budgets
        categories = {
            'Food': 'food_budget',
            'Transportation': 'transportation_budget',
            'Entertainment': 'entertainment_budget',
            'Other': 'other_budget'
        }
        
        for category_name, budget_field in categories.items():
            category_budget = float(budget[budget_field] or 0)
            if category_budget <= 0:
                continue
            
            category_spent_row = db.execute(
                '''SELECT COALESCE(SUM(amount), 0) as total
                   FROM transactions 
                   WHERE user_id = ? AND type = 'expense' AND category = ?
                   AND date >= ? AND date <= ?''',
                (user_id, category_name, week_start.isoformat(), week_end.isoformat())
            ).fetchone()
            
            category_spent = float(category_spent_row['total']) if category_spent_row else 0.0
            category_percentage = (category_spent / category_budget * 100) if category_budget > 0 else 0
            
            if category_percentage >= threshold:
                notification_id = NotificationEngine.create_notification(
                    user_id=user_id,
                    notification_type=NotificationEngine.TYPE_OVERSPENDING,
                    title=f'🚨 {category_name} Budget Exceeded!',
                    message=f'You have spent ${category_spent:.2f} of your ${category_budget:.2f} {category_name.lower()} budget ({category_percentage:.0f}%).',
                    severity=NotificationEngine.SEVERITY_CRITICAL,
                    metadata={
                        'budget': category_budget,
                        'spent': category_spent,
                        'percentage': category_percentage,
                        'category': category_name
                    }
                )
                if notification_id:
                    notifications_created.append(notification_id)
        
        return notifications_created
    
    @staticmethod
    def check_budget_warning(user_id):
        """Check if user is approaching budget limit (warning before overspending)"""
        db = get_db()
        settings = NotificationEngine.get_user_settings(user_id)
        
        if not settings.get('enable_budget_warning', True):
            return []
        
        # Get current week dates
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        # Get current budget
        budget = db.execute(
            '''SELECT * FROM budgets 
               WHERE user_id = ? AND week_start_date = ?
               ORDER BY created_at DESC LIMIT 1''',
            (user_id, week_start.isoformat())
        ).fetchone()
        
        if not budget:
            return []
        
        notifications_created = []
        warning_threshold = settings.get('budget_warning_threshold', 90)
        overspending_threshold = settings.get('overspending_threshold', 100)
        
        # Check overall budget
        total_budget = float(budget['total_amount'])
        total_spent_row = db.execute(
            '''SELECT COALESCE(SUM(amount), 0) as total
               FROM transactions 
               WHERE user_id = ? AND type = 'expense'
               AND date >= ? AND date <= ?''',
            (user_id, week_start.isoformat(), week_end.isoformat())
        ).fetchone()
        
        total_spent = float(total_spent_row['total']) if total_spent_row else 0.0
        spending_percentage = (total_spent / total_budget * 100) if total_budget > 0 else 0
        
        # Only warn if between warning threshold and overspending threshold
        if warning_threshold <= spending_percentage < overspending_threshold:
            remaining = total_budget - total_spent
            notification_id = NotificationEngine.create_notification(
                user_id=user_id,
                notification_type=NotificationEngine.TYPE_BUDGET_WARNING,
                title='⚠️ Budget Warning',
                message=f'You have used {spending_percentage:.0f}% of your weekly budget. ${remaining:.2f} remaining.',
                severity=NotificationEngine.SEVERITY_WARNING,
                metadata={
                    'budget': total_budget,
                    'spent': total_spent,
                    'percentage': spending_percentage,
                    'remaining': remaining,
                    'category': 'overall'
                }
            )
            if notification_id:
                notifications_created.append(notification_id)
        
        # Check category budgets
        categories = {
            'Food': 'food_budget',
            'Transportation': 'transportation_budget',
            'Entertainment': 'entertainment_budget',
            'Other': 'other_budget'
        }
        
        for category_name, budget_field in categories.items():
            category_budget = float(budget[budget_field] or 0)
            if category_budget <= 0:
                continue
            
            category_spent_row = db.execute(
                '''SELECT COALESCE(SUM(amount), 0) as total
                   FROM transactions 
                   WHERE user_id = ? AND type = 'expense' AND category = ?
                   AND date >= ? AND date <= ?''',
                (user_id, category_name, week_start.isoformat(), week_end.isoformat())
            ).fetchone()
            
            category_spent = float(category_spent_row['total']) if category_spent_row else 0.0
            category_percentage = (category_spent / category_budget * 100) if category_budget > 0 else 0
            
            if warning_threshold <= category_percentage < overspending_threshold:
                remaining = category_budget - category_spent
                notification_id = NotificationEngine.create_notification(
                    user_id=user_id,
                    notification_type=NotificationEngine.TYPE_BUDGET_WARNING,
                    title=f'⚠️ {category_name} Budget Warning',
                    message=f'You have used {category_percentage:.0f}% of your {category_name.lower()} budget. ${remaining:.2f} remaining.',
                    severity=NotificationEngine.SEVERITY_WARNING,
                    metadata={
                        'budget': category_budget,
                        'spent': category_spent,
                        'percentage': category_percentage,
                        'remaining': remaining,
                        'category': category_name
                    }
                )
                if notification_id:
                    notifications_created.append(notification_id)
        
        return notifications_created
    
    @staticmethod
    def check_unusual_spending(user_id, category, amount):
        """Check if a transaction amount is unusually high compared to average"""
        db = get_db()
        settings = NotificationEngine.get_user_settings(user_id)
        
        if not settings.get('enable_unusual_spending', True):
            return None
        
        multiplier = settings.get('unusual_spending_multiplier', 2.0)
        
        # Calculate average transaction amount for this category (last 30 days)
        thirty_days_ago = (datetime.now().date() - timedelta(days=30)).isoformat()
        
        avg_row = db.execute(
            '''SELECT AVG(amount) as avg_amount, COUNT(*) as count
               FROM transactions 
               WHERE user_id = ? AND type = 'expense' AND category = ?
               AND date >= ?''',
            (user_id, category, thirty_days_ago)
        ).fetchone()
        
        if not avg_row or avg_row['count'] < 3:  # Need at least 3 transactions for comparison
            return None
        
        avg_amount = float(avg_row['avg_amount'])
        
        # Check if current transaction is unusually high
        if amount >= (avg_amount * multiplier):
            notification_id = NotificationEngine.create_notification(
                user_id=user_id,
                notification_type=NotificationEngine.TYPE_UNUSUAL_SPENDING,
                title='💰 Unusual Spending Detected',
                message=f'Your ${amount:.2f} {category} expense is {(amount/avg_amount):.1f}x higher than your average (${avg_amount:.2f}).',
                severity=NotificationEngine.SEVERITY_INFO,
                metadata={
                    'amount': amount,
                    'average': avg_amount,
                    'multiplier': amount / avg_amount,
                    'category': category
                }
            )
            return notification_id
        
        return None
    
    @staticmethod
    def get_notifications(user_id, unread_only=False, limit=50):
        """Get notifications for a user"""
        db = get_db()
        
        query = '''SELECT * FROM notifications WHERE user_id = ?'''
        params = [user_id]
        
        if unread_only:
            query += ' AND is_read = 0'
        
        query += ' ORDER BY created_at DESC LIMIT ?'
        params.append(limit)
        
        notifications = db.execute(query, params).fetchall()
        
        # Convert to list of dicts and parse metadata
        result = []
        for notif in notifications:
            notif_dict = dict(notif)
            if notif_dict['metadata']:
                try:
                    notif_dict['metadata'] = json.loads(notif_dict['metadata'])
                except:
                    notif_dict['metadata'] = {}
            result.append(notif_dict)
        
        return result
    
    @staticmethod
    def get_unread_count(user_id):
        """Get count of unread notifications"""
        db = get_db()
        count_row = db.execute(
            'SELECT COUNT(*) as count FROM notifications WHERE user_id = ? AND is_read = 0',
            (user_id,)
        ).fetchone()
        return count_row['count'] if count_row else 0
    
    @staticmethod
    def mark_as_read(notification_id, user_id):
        """Mark a notification as read"""
        db = get_db()
        db.execute(
            '''UPDATE notifications 
               SET is_read = 1, read_at = ? 
               WHERE id = ? AND user_id = ?''',
            (datetime.now().isoformat(), notification_id, user_id)
        )
        db.commit()
    
    @staticmethod
    def mark_all_as_read(user_id):
        """Mark all notifications as read for a user"""
        db = get_db()
        db.execute(
            '''UPDATE notifications 
               SET is_read = 1, read_at = ? 
               WHERE user_id = ? AND is_read = 0''',
            (datetime.now().isoformat(), user_id)
        )
        db.commit()
    
    @staticmethod
    def delete_notification(notification_id, user_id):
        """Delete a notification"""
        db = get_db()
        db.execute(
            'DELETE FROM notifications WHERE id = ? AND user_id = ?',
            (notification_id, user_id)
        )
        db.commit()
    
    @staticmethod
    def clear_all_notifications(user_id):
        """Delete all notifications for a user"""
        db = get_db()
        db.execute(
            'DELETE FROM notifications WHERE user_id = ?',
            (user_id,)
        )
        db.commit()
    
    @staticmethod
    def update_settings(user_id, settings_data):
        """Update notification settings for a user"""
        db = get_db()
        
        # Build UPDATE query dynamically based on provided settings
        allowed_fields = [
            'enable_overspending', 'enable_budget_warning', 'enable_goal_achieved',
            'enable_subscription_reminder', 'enable_unusual_spending',
            'overspending_threshold', 'budget_warning_threshold', 'unusual_spending_multiplier',
            'method_in_app', 'method_email', 'method_push',
            'daily_digest', 'max_daily_notifications'
        ]
        
        update_fields = []
        params = []
        
        for field in allowed_fields:
            if field in settings_data:
                update_fields.append(f'{field} = ?')
                params.append(settings_data[field])
        
        if not update_fields:
            return False
        
        # Add updated_at
        update_fields.append('updated_at = ?')
        params.append(datetime.now().isoformat())
        
        # Add user_id for WHERE clause
        params.append(user_id)
        
        query = f'''UPDATE notification_settings 
                    SET {', '.join(update_fields)}
                    WHERE user_id = ?'''
        
        db.execute(query, params)
        db.commit()
        return True
