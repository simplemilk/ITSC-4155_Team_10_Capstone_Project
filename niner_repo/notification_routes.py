"""
Notification Routes Blueprint
API endpoints for managing notifications
"""

from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash
from auth import login_required
from db import get_db
from notifications import NotificationEngine
import json

bp = Blueprint('notifications', __name__, url_prefix='/notifications')


@bp.route('/')
@login_required
def index():
    """Notification center page"""
    from flask import g
    notifications = NotificationEngine.get_notifications(g.user['id'])
    unread_count = NotificationEngine.get_unread_count(g.user['id'])
    
    return render_template('notifications/center.html', 
                         notifications=notifications,
                         unread_count=unread_count)


@bp.route('/api/list')
@login_required
def api_list():
    """API endpoint to get notifications as JSON"""
    from flask import g
    unread_only = request.args.get('unread_only', 'false').lower() == 'true'
    limit = int(request.args.get('limit', 50))
    
    notifications = NotificationEngine.get_notifications(g.user['id'], unread_only, limit)
    unread_count = NotificationEngine.get_unread_count(g.user['id'])
    
    return jsonify({
        'success': True,
        'notifications': notifications,
        'unread_count': unread_count
    })


@bp.route('/api/unread-count')
@login_required
def api_unread_count():
    """API endpoint to get unread notification count"""
    from flask import g
    count = NotificationEngine.get_unread_count(g.user['id'])
    return jsonify({
        'success': True,
        'count': count
    })


@bp.route('/api/mark-read/<int:notification_id>', methods=['POST'])
@login_required
def api_mark_read(notification_id):
    """Mark a notification as read"""
    from flask import g
    try:
        NotificationEngine.mark_as_read(notification_id, g.user['id'])
        return jsonify({
            'success': True,
            'message': 'Notification marked as read'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@bp.route('/api/mark-all-read', methods=['POST'])
@login_required
def api_mark_all_read():
    """Mark all notifications as read"""
    from flask import g
    try:
        NotificationEngine.mark_all_as_read(g.user['id'])
        return jsonify({
            'success': True,
            'message': 'All notifications marked as read'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@bp.route('/api/delete/<int:notification_id>', methods=['POST', 'DELETE'])
@login_required
def api_delete(notification_id):
    """Delete a notification"""
    from flask import g
    try:
        NotificationEngine.delete_notification(notification_id, g.user['id'])
        return jsonify({
            'success': True,
            'message': 'Notification deleted'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@bp.route('/api/clear-all', methods=['POST', 'DELETE'])
@login_required
def api_clear_all():
    """Clear all notifications"""
    from flask import g
    try:
        NotificationEngine.clear_all_notifications(g.user['id'])
        return jsonify({
            'success': True,
            'message': 'All notifications cleared'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@bp.route('/settings')
@login_required
def settings():
    """Notification settings page"""
    from flask import g
    user_settings = NotificationEngine.get_user_settings(g.user['id'])
    return render_template('notifications/settings.html', settings=user_settings)


@bp.route('/api/settings', methods=['GET'])
@login_required
def api_get_settings():
    """Get notification settings as JSON"""
    from flask import g
    settings = NotificationEngine.get_user_settings(g.user['id'])
    return jsonify({
        'success': True,
        'settings': settings
    })


@bp.route('/api/settings', methods=['POST', 'PUT'])
@login_required
def api_update_settings():
    """Update notification settings"""
    from flask import g
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        success = NotificationEngine.update_settings(g.user['id'], data)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Settings updated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No valid settings to update'
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@bp.route('/api/check-budget', methods=['POST'])
@login_required
def api_check_budget():
    """Manually trigger budget check (useful for testing)"""
    from flask import g
    try:
        # Check for warnings first, then overspending
        warnings = NotificationEngine.check_budget_warning(g.user['id'])
        overspending = NotificationEngine.check_overspending(g.user['id'])
        
        all_notifications = warnings + overspending
        
        return jsonify({
            'success': True,
            'message': f'Created {len(all_notifications)} notification(s)',
            'notification_ids': all_notifications
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
