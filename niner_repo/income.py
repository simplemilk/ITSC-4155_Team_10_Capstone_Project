from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, g
from auth import login_required
from db import get_db
import sqlite3

# Create the blueprint - this is crucial!
bp = Blueprint('income', __name__, url_prefix='/income')

@bp.route('/')
@login_required
def index():
    """Display income records for the logged-in user"""
    try:
        db = get_db()
        
        # Get income records with category information
        income_records = db.execute('''
            SELECT i.*, ic.name as category_name 
            FROM income i 
            LEFT JOIN income_category ic ON i.category_id = ic.id
            WHERE i.user_id = ? AND i.is_active = 1
            ORDER BY i.date DESC
        ''', (g.user['id'],)).fetchall()
        
        # Calculate total income
        total_income = sum(record['amount'] for record in income_records) if income_records else 0
        
        # Get income categories for the form - create basic categories if none exist
        try:
            categories = db.execute(
                'SELECT * FROM income_category ORDER BY name'
            ).fetchall()
        except sqlite3.OperationalError:
            # Create basic categories if table doesn't exist
            categories = [
                {'id': 1, 'name': 'Salary'},
                {'id': 2, 'name': 'Freelance'},
                {'id': 3, 'name': 'Investment'},
                {'id': 4, 'name': 'Other'}
            ]
        
        return render_template('home/income.html', 
                             income_records=income_records or [],
                             total_income=total_income,
                             categories=categories)
        
    except Exception as e:
        print(f"Error in income index: {e}")
        flash(f'Error loading income data: {str(e)}', 'error')
        return render_template('home/index.html', 
                             income_records=[],
                             total_income=0,
                             categories=[])

@bp.route('/add', methods=['POST'])
@login_required
def add():
    """Add a new income record"""
    try:
        source = request.form['source']
        amount = float(request.form['amount'])
        category_id = request.form.get('category_id', 1)
        description = request.form.get('description', '')
        date = request.form['date']
        is_recurring = 'is_recurring' in request.form
        recurrence_period = request.form.get('recurrence_period') if is_recurring else None
        
        db = get_db()
        db.execute('''
            INSERT INTO income (user_id, category_id, amount, source, description, date, 
                              is_recurring, recurrence_period, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (g.user['id'], category_id, amount, source, description, date,
              is_recurring, recurrence_period, g.user['id']))
        db.commit()
        
        flash('Income record added successfully!', 'success')
        
    except Exception as e:
        print(f"Error adding income: {e}")
        flash(f'Error adding income: {str(e)}', 'error')
    
    return redirect(url_for('income.index'))

@bp.route('/api')
@login_required
def api():
    """API endpoint that returns JSON data"""
    try:
        db = get_db()
        
        income_records = db.execute('''
            SELECT * FROM income 
            WHERE user_id = ? 
            ORDER BY date DESC
        ''', (g.user['id'],)).fetchall()
        
        # Convert to list of dictionaries
        data = [dict(record) for record in income_records]
        
        return jsonify({
            'data': data,
            'total': len(data)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Add debug function to check if blueprint is working
@bp.route('/test')
def test():
    """Test route to verify blueprint is working"""
    return "Income blueprint is working!"

@bp.route('/delete/<int:income_id>', methods=['POST'])
@login_required
def delete(income_id):
    """Delete an income record"""
    try:
        db = get_db()
        
        # Check if the income record exists for the current user
        income = db.execute('SELECT * FROM income WHERE id = ? AND user_id = ?', (income_id, g.user['id'])).fetchone()
        
        if not income:
            flash('Income record not found or you do not have permission to delete it.', 'error')
            return redirect(url_for('income.index'))
        
        db.execute('UPDATE income SET is_active = 0 WHERE id = ?', (income_id,))
        db.commit()

        flash('Income record deleted successfully!', 'success')
        return redirect(url_for('income.index'))
        
    except Exception as e:
        flash(f'Error deleting income record: {str(e)}', 'error')
        return redirect(url_for('income.index'))
