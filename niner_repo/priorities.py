from flask import Blueprint, request, jsonify, render_template, g
from db import get_db
from auth import login_required
from datetime import datetime
import json

bp = Blueprint('priorities', __name__, url_prefix='/finance/priorities')

PRIORITY_CATEGORIES = {
    'Save More': {
        'icon': '💰',
        'description': 'Build your savings and emergency fund',
        'color': '#10b981'
    },
    'Reduce Debt': {
        'icon': '📉',
        'description': 'Pay off loans and credit card balances',
        'color': '#ef4444'
    },
    'Invest More': {
        'icon': '📈',
        'description': 'Grow wealth through investments',
        'color': '#3b82f6'
    },
    'Control Spending': {
        'icon': '🎯',
        'description': 'Manage expenses and stick to budget',
        'color': '#f59e0b'
    }
}

@bp.route('/select')
@login_required
def select_priority():
    """Render the priority selection page"""
    return render_template('home/priority.html')

@bp.route('', methods=['GET'])
@login_required
def get_priorities():
    """Get user's current priorities"""
    db = get_db()
    
    priorities = db.execute(
        '''SELECT p.*, 
           COUNT(DISTINCT a.id) as actions_count
           FROM user_priorities p
           LEFT JOIN user_priority_actions a ON p.id = a.priority_id
           WHERE p.user_id = ?
           GROUP BY p.id
           ORDER BY p.importance_level DESC, p.created_at DESC''',
        (g.user['id'],)
    ).fetchall()
    
    return jsonify([{
        'id': p['id'],
        'priority_type': p['priority_type'],
        'importance_level': p['importance_level'],
        'target_amount': p['target_amount'],
        'target_date': p['target_date'],
        'notes': p['notes'],
        'actions_count': p['actions_count'],
        'created_at': p['created_at'],
        'updated_at': p['updated_at']
    } for p in priorities])

@bp.route('', methods=['POST'])
@login_required
def save_priority():
    """Save or update user's priority"""
    data = request.get_json()
    priority = data.get('priority')
    importance_level = data.get('importance_level', 1)
    target_amount = data.get('target_amount')
    target_date = data.get('target_date')
    notes = data.get('notes', '')
    
    if not priority or priority not in PRIORITY_CATEGORIES:
        return jsonify({'error': 'Invalid priority type'}), 400
    
    db = get_db()
    
    # Check if priority already exists
    existing = db.execute(
        'SELECT id FROM user_priorities WHERE user_id = ? AND priority_type = ?',
        (g.user['id'], priority)
    ).fetchone()
    
    try:
        if existing:
            # Update existing priority
            db.execute(
                '''UPDATE user_priorities 
                   SET importance_level = ?, target_amount = ?, target_date = ?, 
                       notes = ?, updated_at = CURRENT_TIMESTAMP
                   WHERE id = ?''',
                (importance_level, target_amount, target_date, notes, existing['id'])
            )
            priority_id = existing['id']
            message = f'{priority} priority updated successfully'
        else:
            # Insert new priority
            cursor = db.execute(
                '''INSERT INTO user_priorities 
                   (user_id, priority_type, importance_level, target_amount, target_date, notes)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (g.user['id'], priority, importance_level, target_amount, target_date, notes)
            )
            priority_id = cursor.lastrowid
            message = f'{priority} priority set successfully'
        
        db.commit()
        
        # Get personalized suggestions
        suggestions = get_personalized_suggestions(priority, g.user['id'])
        
        return jsonify({
            'message': message,
            'priority_id': priority_id,
            'suggestions': suggestions
        }), 200
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:priority_id>', methods=['DELETE'])
@login_required
def delete_priority(priority_id):
    """Delete a priority"""
    db = get_db()
    
    # Verify ownership
    priority = db.execute(
        'SELECT id FROM user_priorities WHERE id = ? AND user_id = ?',
        (priority_id, g.user['id'])
    ).fetchone()
    
    if not priority:
        return jsonify({'error': 'Priority not found'}), 404
    
    try:
        db.execute('DELETE FROM user_priorities WHERE id = ?', (priority_id,))
        db.commit()
        return jsonify({'message': 'Priority deleted successfully'}), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/suggestions')
@login_required
def get_all_suggestions():
    """Get suggestions for all user's priorities"""
    db = get_db()
    
    # Get user's priorities
    priorities = db.execute(
        'SELECT priority_type FROM user_priorities WHERE user_id = ? ORDER BY importance_level DESC',
        (g.user['id'],)
    ).fetchall()
    
    all_suggestions = {}
    for priority in priorities:
        priority_type = priority['priority_type']
        all_suggestions[priority_type] = get_personalized_suggestions(priority_type, g.user['id'])
    
    return jsonify(all_suggestions)

def get_personalized_suggestions(priority_type, user_id):
    """Get personalized suggestions based on priority and user's financial data"""
    db = get_db()
    
    # Get base suggestions
    suggestions = db.execute(
        '''SELECT suggestion_text, category, min_amount, max_amount 
           FROM priority_suggestions 
           WHERE priority_type = ?
           ORDER BY RANDOM()
           LIMIT 5''',
        (priority_type,)
    ).fetchall()
    
    # Get user's financial stats
    stats = get_user_financial_stats(user_id)
    
    # Customize suggestions based on user's situation
    personalized = []
    for suggestion in suggestions:
        custom_suggestion = {
            'text': suggestion['suggestion_text'],
            'category': suggestion['category'],
            'relevance_score': calculate_relevance(suggestion, stats, priority_type)
        }
        
        # Add specific amounts if applicable
        if suggestion['min_amount'] and suggestion['max_amount']:
            recommended_amount = calculate_recommended_amount(
                suggestion['min_amount'], 
                suggestion['max_amount'], 
                stats
            )
            custom_suggestion['recommended_amount'] = recommended_amount
        
        personalized.append(custom_suggestion)
    
    # Sort by relevance
    personalized.sort(key=lambda x: x['relevance_score'], reverse=True)
    
    return personalized

def get_user_financial_stats(user_id):
    """Get user's financial statistics"""
    db = get_db()
    
    # Get total income
    income = db.execute(
        'SELECT COALESCE(SUM(amount), 0) as total FROM income WHERE user_id = ?',
        (user_id,)
    ).fetchone()
    
    # Get total expenses
    expenses = db.execute(
        'SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE user_id = ? AND type = "expense"',
        (user_id,)
    ).fetchone()
    
    # Get savings/investments
    savings = db.execute(
        'SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE user_id = ? AND category IN ("Savings", "Investment")',
        (user_id,)
    ).fetchone()
    
    return {
        'monthly_income': income['total'] if income else 0,
        'monthly_expenses': expenses['total'] if expenses else 0,
        'total_savings': savings['total'] if savings else 0,
        'savings_rate': (savings['total'] / income['total'] * 100) if income and income['total'] > 0 else 0
    }

def calculate_relevance(suggestion, stats, priority_type):
    """Calculate how relevant a suggestion is to the user's current situation"""
    relevance = 50  # Base score
    
    if priority_type == 'Save More':
        if stats['savings_rate'] < 10:
            relevance += 30
        elif stats['savings_rate'] < 20:
            relevance += 20
    
    elif priority_type == 'Reduce Debt':
        # Could integrate debt data if available
        relevance += 25
    
    elif priority_type == 'Invest More':
        if stats['savings_rate'] > 20:
            relevance += 30
        elif stats['total_savings'] > 5000:
            relevance += 20
    
    elif priority_type == 'Control Spending':
        if stats['monthly_expenses'] > stats['monthly_income'] * 0.7:
            relevance += 40
    
    return min(relevance, 100)

def calculate_recommended_amount(min_amount, max_amount, stats):
    """Calculate recommended amount based on user's income"""
    income = stats['monthly_income']
    
    if income == 0:
        return min_amount
    
    # Recommend based on percentage of income
    recommended = income * 0.1  # 10% of income
    
    # Clamp to min/max
    return max(min_amount, min(recommended, max_amount))

@bp.route('/actions', methods=['POST'])
@login_required
def log_action():
    """Log an action taken towards a priority"""
    data = request.get_json()
    priority_id = data.get('priority_id')
    action_taken = data.get('action')
    notes = data.get('notes', '')
    
    if not priority_id or not action_taken:
        return jsonify({'error': 'Missing required fields'}), 400
    
    db = get_db()
    
    # Verify ownership
    priority = db.execute(
        'SELECT id FROM user_priorities WHERE id = ? AND user_id = ?',
        (priority_id, g.user['id'])
    ).fetchone()
    
    if not priority:
        return jsonify({'error': 'Priority not found'}), 404
    
    try:
        db.execute(
            '''INSERT INTO user_priority_actions (user_id, priority_id, action_taken, notes)
               VALUES (?, ?, ?, ?)''',
            (g.user['id'], priority_id, action_taken, notes)
        )
        db.commit()
        return jsonify({'message': 'Action logged successfully'}), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500