from flask import (
    Blueprint, g, request, jsonify, render_template, redirect, url_for, flash
)
from werkzeug.exceptions import abort
from auth import login_required
from db import get_db
from datetime import datetime
import sqlite3
from decimal import Decimal, InvalidOperation

try:
    from auth import login_required
    from db import get_db
except ImportError:
    def login_required(f):
        return f
    def get_db():
        return None

bp = Blueprint('income', __name__)

def get_income(id, check_author=True):
    """Get a specific income record by ID."""
    income = get_db().execute(
        'SELECT * FROM v_active_income WHERE id = ?', (id,)
    ).fetchone()

    if income is None:
        abort(404, f"Income record {id} doesn't exist.")

    if check_author and income['user_id'] != g.user['id']:
        abort(403, "You don't have permission to access this record.")

    return income

@bp.route('/income/create', methods=['POST'])
@login_required
def create():
    """Create a new income record."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Validate required fields
        required_fields = ['amount', 'source', 'category_id']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

        # Validate and convert amount
        try:
            amount = Decimal(str(data['amount']))
            if amount <= 0:
                return jsonify({'error': 'Amount must be greater than 0'}), 400
        except (InvalidOperation, TypeError):
            return jsonify({'error': 'Invalid amount format'}), 400

        # Validate source
        source = str(data['source']).strip()
        if not source or len(source) > 100:
            return jsonify({'error': 'Source must be between 1 and 100 characters'}), 400

        # Validate date
        try:
            date = datetime.strptime(data.get('date', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d').date()
            if date > datetime.now().date():
                return jsonify({'error': 'Date cannot be in the future'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

        # Validate category
        db = get_db()
        category = db.execute(
            'SELECT id FROM income_category WHERE id = ? AND is_active = 1',
            (data['category_id'],)
        ).fetchone()
        if not category:
            return jsonify({'error': 'Invalid category'}), 400

        # Handle recurring income validation
        is_recurring = data.get('is_recurring', False)
        recurrence_period = data.get('recurrence_period')
        next_recurrence_date = None

        if is_recurring:
            if not recurrence_period or recurrence_period not in [
                'daily', 'weekly', 'biweekly', 'monthly', 'quarterly', 'annually'
            ]:
                return jsonify({'error': 'Invalid recurrence period'}), 400
            
            try:
                next_recurrence_date = datetime.strptime(
                    data['next_recurrence_date'], '%Y-%m-%d'
                ).date()
                if next_recurrence_date <= date:
                    return jsonify({'error': 'Next recurrence date must be after the income date'}), 400
            except (KeyError, ValueError):
                return jsonify({'error': 'Invalid next recurrence date format'}), 400

        # Insert the record
        try:
            cursor = db.execute(
                '''INSERT INTO income (
                    user_id, category_id, amount, source, description,
                    date, is_recurring, recurrence_period, next_recurrence_date,
                    created_by, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)''',
                (g.user['id'], data['category_id'], amount, source,
                 data.get('description', ''), date, is_recurring,
                 recurrence_period, next_recurrence_date, g.user['id'])
            )
            db.commit()
            
            # Get the inserted record
            income = get_income(cursor.lastrowid, check_author=False)
            
            return jsonify({
                'message': 'Income recorded successfully',
                'data': dict(income)
            }), 201

        except sqlite3.Error as e:
            db.rollback()
            return jsonify({'error': f'Database error: {str(e)}'}), 500

    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

@bp.route('/income', methods=['GET'])
@login_required
def list_all():
    """Get all income records for the current user."""
    try:
        db = get_db()
        if db is None:
            flash('Database connection not available.', 'error')
            return jsonify({'error': 'Database connection not available'}), 503

        # Get query parameters for filtering
        category_id = request.args.get('category_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        is_recurring = request.args.get('is_recurring', type=int)

        query = 'SELECT * FROM v_active_income WHERE user_id = ?'
        params = [g.user['id']]

        # Add filters
        if category_id:
            query += ' AND category_id = ?'
            params.append(category_id)
        if start_date:
            query += ' AND date >= ?'
            params.append(start_date)
        if end_date:
            query += ' AND date <= ?'
            params.append(end_date)
        if is_recurring is not None:
            query += ' AND is_recurring = ?'
            params.append(is_recurring)

        query += ' ORDER BY date DESC, created_at DESC'

        income_entries = get_db().execute(query, params).fetchall()

        return jsonify({
            'data': [dict(entry) for entry in income_entries],
            'total': len(income_entries)
        })

    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@bp.route('/<int:id>', methods=['GET'])
@login_required
def get(id):
    """Get a specific income record."""
    try:
        income = get_income(id)
        return jsonify({'data': dict(income)})
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@bp.route('/<int:id>', methods=['PUT', 'PATCH'])
@login_required
def update(id):
    """Update an income record."""
    try:
        income = get_income(id)  # Verify existence and ownership
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        updates = []
        params = []
        
        # Handle amount update
        if 'amount' in data:
            try:
                amount = Decimal(str(data['amount']))
                if amount <= 0:
                    return jsonify({'error': 'Amount must be greater than 0'}), 400
                updates.append('amount = ?')
                params.append(amount)
            except (InvalidOperation, TypeError):
                return jsonify({'error': 'Invalid amount format'}), 400

        # Handle source update
        if 'source' in data:
            source = str(data['source']).strip()
            if not source or len(source) > 100:
                return jsonify({'error': 'Source must be between 1 and 100 characters'}), 400
            updates.append('source = ?')
            params.append(source)

        # Handle category update
        if 'category_id' in data:
            category = get_db().execute(
                'SELECT id FROM income_category WHERE id = ? AND is_active = 1',
                (data['category_id'],)
            ).fetchone()
            if not category:
                return jsonify({'error': 'Invalid category'}), 400
            updates.append('category_id = ?')
            params.append(data['category_id'])

        # Handle date update
        if 'date' in data:
            try:
                date = datetime.strptime(data['date'], '%Y-%m-%d').date()
                if date > datetime.now().date():
                    return jsonify({'error': 'Date cannot be in the future'}), 400
                updates.append('date = ?')
                params.append(date)
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

        # Handle description update
        if 'description' in data:
            updates.append('description = ?')
            params.append(str(data.get('description', '')).strip())

        # Handle recurring income updates
        if 'is_recurring' in data:
            is_recurring = bool(data['is_recurring'])
            updates.append('is_recurring = ?')
            params.append(is_recurring)

            if is_recurring:
                if 'recurrence_period' not in data:
                    return jsonify({'error': 'Recurrence period required for recurring income'}), 400
                if data['recurrence_period'] not in [
                    'daily', 'weekly', 'biweekly', 'monthly', 'quarterly', 'annually'
                ]:
                    return jsonify({'error': 'Invalid recurrence period'}), 400
                
                updates.append('recurrence_period = ?')
                params.append(data['recurrence_period'])

                try:
                    next_date = datetime.strptime(
                        data['next_recurrence_date'], '%Y-%m-%d'
                    ).date()
                    if next_date <= datetime.now().date():
                        return jsonify({'error': 'Next recurrence date must be in the future'}), 400
                    updates.append('next_recurrence_date = ?')
                    params.append(next_date)
                except (KeyError, ValueError):
                    return jsonify({'error': 'Invalid next recurrence date format'}), 400
            else:
                updates.extend(['recurrence_period = NULL', 'next_recurrence_date = NULL'])

        if not updates:
            return jsonify({'error': 'No valid fields to update'}), 400

        # Add updated_by to the update
        updates.append('updated_by = ?')
        params.append(g.user['id'])
        
        # Add the record ID to params
        params.append(id)

        db = get_db()
        db.execute(
            f'UPDATE income SET {", ".join(updates)} WHERE id = ?',
            params
        )
        db.commit()

        # Get the updated record
        updated_income = get_income(id, check_author=False)
        
        return jsonify({
            'message': 'Income updated successfully',
            'data': dict(updated_income)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete(id):
    """Soft delete an income record."""
    try:
        income = get_income(id)  # Verify existence and ownership
        
        db = get_db()
        db.execute(
            'UPDATE income SET is_active = 0, updated_by = ? WHERE id = ?',
            (g.user['id'], id)
        )
        db.commit()
        
        return jsonify({
            'message': 'Income record deleted successfully',
            'id': id
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/categories', methods=['GET'])
@login_required
def list_categories():
    """Get all active income categories."""
    try:
        categories = get_db().execute(
            'SELECT * FROM income_category WHERE is_active = 1 ORDER BY name'
        ).fetchall()
        
        return jsonify({
            'data': [dict(category) for category in categories]
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/summary', methods=['GET'])
@login_required
def get_summary():
    """Get income summary statistics."""
    try:
        # Get query parameters for filtering
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))

        query = '''
            SELECT 
                SUM(amount) as total_income,
                COUNT(*) as total_entries,
                category_name,
                SUM(CASE WHEN is_recurring = 1 THEN amount ELSE 0 END) as recurring_income,
                SUM(CASE WHEN is_recurring = 0 THEN amount ELSE 0 END) as non_recurring_income
            FROM v_active_income 
            WHERE user_id = ?
        '''
        params = [g.user['id']]

        if start_date:
            query += ' AND date >= ?'
            params.append(start_date)
        if end_date:
            query += ' AND date <= ?'
            params.append(end_date)

        query += ' GROUP BY category_name'

        summary = get_db().execute(query, params).fetchall()

        # Calculate totals
        total_query = '''
            SELECT 
                SUM(amount) as grand_total,
                COUNT(*) as total_records,
                COUNT(DISTINCT category_id) as total_categories
            FROM v_active_income 
            WHERE user_id = ?
        '''
        if start_date:
            total_query += ' AND date >= ?'
        if end_date:
            total_query += ' AND date <= ?'

        totals = get_db().execute(total_query, params).fetchone()

        return jsonify({
            'data': {
                'categories': [dict(entry) for entry in summary],
                'totals': dict(totals)
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500