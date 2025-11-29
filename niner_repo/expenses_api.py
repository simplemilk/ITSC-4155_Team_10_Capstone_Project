"""
Expenses API Blueprint
Fast expense logging with validation and integration
"""

from flask import Blueprint, jsonify, request, g
from auth import login_required
from db import get_db
from datetime import datetime
from decimal import Decimal, InvalidOperation
from notifications import NotificationEngine

bp = Blueprint('expenses_api', __name__, url_prefix='/api/expenses')


@bp.route('', methods=['POST'])
@login_required
def create_expense():
    """
    Create a new expense
    POST /api/expenses
    
    Body:
    {
        "amount": 25.50,
        "category": "Food",
        "description": "Lunch at McDonald's",
        "date": "2025-11-12"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Extract and validate fields
        amount = data.get('amount')
        category = data.get('category')
        description = data.get('description', '').strip()
        date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        # Validation
        errors = []
        
        # Validate amount
        if amount is None:
            errors.append('Amount is required')
        else:
            try:
                amount = Decimal(str(amount))
                if amount <= 0:
                    errors.append('Amount must be greater than 0')
                elif amount > 999999:
                    errors.append('Amount is too large')
            except (InvalidOperation, ValueError):
                errors.append('Invalid amount format')
        
        # Validate category
        valid_categories = ['Food', 'Transportation', 'Entertainment', 'Shopping', 
                          'Health', 'Utilities', 'Education', 'Other']
        if not category:
            errors.append('Category is required')
        elif category not in valid_categories:
            errors.append(f'Invalid category. Must be one of: {", ".join(valid_categories)}')
        
        # Validate date
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            errors.append('Invalid date format. Use YYYY-MM-DD')
        
        # Validate description length
        if len(description) > 200:
            errors.append('Description must be 200 characters or less')
        
        # Return validation errors
        if errors:
            return jsonify({
                'success': False,
                'error': 'Validation failed',
                'errors': errors
            }), 400
        
        # Save to database
        db = get_db()
        user_id = g.user['id']
        
        cursor = db.execute(
            '''INSERT INTO transactions 
               (user_id, description, amount, category, type, date)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (user_id, description, float(amount), category, 'expense', date)
        )
        db.commit()
        
        expense_id = cursor.lastrowid
        
        # Get the created expense
        expense = db.execute(
            'SELECT * FROM transactions WHERE id = ?',
            (expense_id,)
        ).fetchone()
        
        # Trigger notification checks (async, don't block response)
        try:
            NotificationEngine.check_unusual_spending(user_id, category, float(amount))
            NotificationEngine.check_budget_warning(user_id)
            NotificationEngine.check_overspending(user_id)
        except Exception as notif_error:
            print(f"Notification error: {notif_error}")
        
        # Return success response
        return jsonify({
            'success': True,
            'message': 'Expense added successfully',
            'expense': {
                'id': expense['id'],
                'amount': float(expense['amount']),
                'category': expense['category'],
                'description': expense['description'],
                'date': expense['date'],
                'created_at': expense['created_at']
            }
        }), 201
        
    except Exception as e:
        print(f"Error creating expense: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@bp.route('/recent', methods=['GET'])
@login_required
def get_recent_expenses():
    """
    Get recent expenses for the user
    GET /api/expenses/recent?limit=5
    """
    try:
        limit = request.args.get('limit', 5, type=int)
        if limit > 50:
            limit = 50
        
        db = get_db()
        user_id = g.user['id']
        
        expenses = db.execute(
            '''SELECT * FROM transactions 
               WHERE user_id = ? AND type = 'expense'
               ORDER BY date DESC, created_at DESC
               LIMIT ?''',
            (user_id, limit)
        ).fetchall()
        
        expense_list = []
        for expense in expenses:
            expense_list.append({
                'id': expense['id'],
                'amount': float(expense['amount']),
                'category': expense['category'],
                'description': expense['description'],
                'date': expense['date'],
                'created_at': expense['created_at']
            })
        
        return jsonify({
            'success': True,
            'expenses': expense_list
        })
        
    except Exception as e:
        print(f"Error getting recent expenses: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@bp.route('/<int:expense_id>', methods=['GET'])
@login_required
def get_expense(expense_id):
    """
    Get a specific expense
    GET /api/expenses/:id
    """
    try:
        db = get_db()
        user_id = g.user['id']
        
        expense = db.execute(
            '''SELECT * FROM transactions 
               WHERE id = ? AND user_id = ? AND type = 'expense' ''',
            (expense_id, user_id)
        ).fetchone()
        
        if not expense:
            return jsonify({
                'success': False,
                'error': 'Expense not found'
            }), 404
        
        return jsonify({
            'success': True,
            'expense': {
                'id': expense['id'],
                'amount': float(expense['amount']),
                'category': expense['category'],
                'description': expense['description'],
                'date': expense['date'],
                'created_at': expense['created_at']
            }
        })
        
    except Exception as e:
        print(f"Error getting expense: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@bp.route('/<int:expense_id>', methods=['PUT', 'PATCH'])
@login_required
def update_expense(expense_id):
    """
    Update an expense
    PUT/PATCH /api/expenses/:id
    """
    try:
        db = get_db()
        user_id = g.user['id']
        
        # Check expense exists and belongs to user
        expense = db.execute(
            '''SELECT * FROM transactions 
               WHERE id = ? AND user_id = ? AND type = 'expense' ''',
            (expense_id, user_id)
        ).fetchone()
        
        if not expense:
            return jsonify({
                'success': False,
                'error': 'Expense not found'
            }), 404
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Build update query dynamically
        update_fields = []
        params = []
        
        if 'amount' in data:
            try:
                amount = Decimal(str(data['amount']))
                if amount <= 0:
                    return jsonify({'success': False, 'error': 'Amount must be greater than 0'}), 400
                update_fields.append('amount = ?')
                params.append(float(amount))
            except (InvalidOperation, ValueError):
                return jsonify({'success': False, 'error': 'Invalid amount'}), 400
        
        valid_categories = ['Food', 'Transportation', 'Entertainment', 'Shopping', 
                          'Health', 'Utilities', 'Education', 'Other']
        if 'category' in data:
            if data['category'] not in valid_categories:
                return jsonify({'success': False, 'error': 'Invalid category'}), 400
            update_fields.append('category = ?')
            params.append(data['category'])
        
        if 'description' in data:
            desc = data['description'].strip()
            if len(desc) > 200:
                return jsonify({'success': False, 'error': 'Description too long'}), 400
            update_fields.append('description = ?')
            params.append(desc)
        
        if 'date' in data:
            try:
                datetime.strptime(data['date'], '%Y-%m-%d')
                update_fields.append('date = ?')
                params.append(data['date'])
            except ValueError:
                return jsonify({'success': False, 'error': 'Invalid date format'}), 400
        
        if not update_fields:
            return jsonify({'success': False, 'error': 'No fields to update'}), 400
        
        # Add expense_id to params
        params.append(expense_id)
        params.append(user_id)
        
        # Execute update
        query = f'''UPDATE transactions 
                    SET {', '.join(update_fields)}
                    WHERE id = ? AND user_id = ?'''
        db.execute(query, params)
        db.commit()
        
        # Get updated expense
        updated_expense = db.execute(
            'SELECT * FROM transactions WHERE id = ?',
            (expense_id,)
        ).fetchone()
        
        return jsonify({
            'success': True,
            'message': 'Expense updated successfully',
            'expense': {
                'id': updated_expense['id'],
                'amount': float(updated_expense['amount']),
                'category': updated_expense['category'],
                'description': updated_expense['description'],
                'date': updated_expense['date']
            }
        })
        
    except Exception as e:
        print(f"Error updating expense: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@bp.route('/<int:expense_id>', methods=['DELETE'])
@login_required
def delete_expense(expense_id):
    """
    Delete an expense
    DELETE /api/expenses/:id
    """
    try:
        db = get_db()
        user_id = g.user['id']
        
        # Check expense exists and belongs to user
        expense = db.execute(
            '''SELECT * FROM transactions 
               WHERE id = ? AND user_id = ? AND type = 'expense' ''',
            (expense_id, user_id)
        ).fetchone()
        
        if not expense:
            return jsonify({
                'success': False,
                'error': 'Expense not found'
            }), 404
        
        # Delete the expense
        db.execute('DELETE FROM transactions WHERE id = ?', (expense_id,))
        db.commit()
        
        return jsonify({
            'success': True,
            'message': 'Expense deleted successfully'
        })
        
    except Exception as e:
        print(f"Error deleting expense: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@bp.route('/categories', methods=['GET'])
@login_required
def get_categories():
    """
    Get list of available expense categories
    GET /api/expenses/categories
    """
    categories = [
        {'value': 'Food', 'label': '🍔 Food', 'icon': '🍔'},
        {'value': 'Transportation', 'label': '🚗 Transportation', 'icon': '🚗'},
        {'value': 'Entertainment', 'label': '🎬 Entertainment', 'icon': '🎬'},
        {'value': 'Shopping', 'label': '🛍️ Shopping', 'icon': '🛍️'},
        {'value': 'Health', 'label': '⚕️ Health', 'icon': '⚕️'},
        {'value': 'Utilities', 'label': '💡 Utilities', 'icon': '💡'},
        {'value': 'Education', 'label': '📚 Education', 'icon': '📚'},
        {'value': 'Other', 'label': '📦 Other', 'icon': '📦'}
    ]
    
    return jsonify({
        'success': True,
        'categories': categories
    })
