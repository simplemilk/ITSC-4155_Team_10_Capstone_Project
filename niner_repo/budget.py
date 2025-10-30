from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, g
from flask_cors import cross_origin
from datetime import datetime, timedelta
from auth import login_required
from db import get_db
import sqlite3

bp = Blueprint('budget', __name__)

@bp.route('/budget')
def index():
    return render_template('home/index.html')

@bp.route('/budget/create')
def create():
    return render_template('home/create.html')


@bp.route('/weekly', methods=['GET'])
@login_required
@cross_origin()
def get_weekly_budget():
    """Get weekly budget data for the current user."""
    try:
        user_id = g.user['id']
        db = get_db()
        
        # Get current week's start and end dates
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        # Get weekly budget
        budget = db.execute('''
            SELECT * FROM weekly_budgets 
            WHERE user_id = ? AND week_start = ?
        ''', (user_id, start_of_week.strftime('%Y-%m-%d'))).fetchone()
        
        if not budget:
            return jsonify({'error': 'No budget found for this week'}), 404
        
        # Get expenses for this week
        expenses = db.execute('''
            SELECT category, SUM(amount) as total_spent
            FROM expenses 
            WHERE user_id = ? AND date BETWEEN ? AND ?
            GROUP BY category
        ''', (user_id, start_of_week.strftime('%Y-%m-%d'), end_of_week.strftime('%Y-%m-%d'))).fetchall()
        
        expenses_dict = {expense['category']: expense['total_spent'] for expense in expenses}
        
        budget_data = {
            'id': budget['id'],
            'week_start': budget['week_start'],
            'week_end': budget['week_end'],
            'total_budget': budget['total_budget'],
            'categories': {
                'food': {
                    'budgeted': budget['food_budget'],
                    'spent': expenses_dict.get('food', 0)
                },
                'transportation': {
                    'budgeted': budget['transportation_budget'],
                    'spent': expenses_dict.get('transportation', 0)
                },
                'entertainment': {
                    'budgeted': budget['entertainment_budget'],
                    'spent': expenses_dict.get('entertainment', 0)
                },
                'other': {
                    'budgeted': budget['other_budget'],
                    'spent': expenses_dict.get('other', 0)
                }
            }
        }
        
        return jsonify(budget_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/weekly', methods=['POST'])
@login_required
@cross_origin()
def create_weekly_budget():
    """Create or update weekly budget."""
    try:
        user_id = g.user['id']
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['total_budget', 'food_budget', 'transportation_budget', 'entertainment_budget', 'other_budget']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Get current week dates
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        db = get_db()
        
        # Check if budget already exists for this week
        existing_budget = db.execute('''
            SELECT id FROM weekly_budgets 
            WHERE user_id = ? AND week_start = ?
        ''', (user_id, start_of_week.strftime('%Y-%m-%d'))).fetchone()
        
        if existing_budget:
            # Update existing budget
            db.execute('''
                UPDATE weekly_budgets 
                SET total_budget = ?, food_budget = ?, transportation_budget = ?, 
                    entertainment_budget = ?, other_budget = ?
                WHERE id = ?
            ''', (data['total_budget'], data['food_budget'], data['transportation_budget'],
                  data['entertainment_budget'], data['other_budget'], existing_budget['id']))
        else:
            # Create new budget
            db.execute('''
                INSERT INTO weekly_budgets 
                (user_id, week_start, week_end, total_budget, food_budget, 
                 transportation_budget, entertainment_budget, other_budget)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, start_of_week.strftime('%Y-%m-%d'), end_of_week.strftime('%Y-%m-%d'),
                  data['total_budget'], data['food_budget'], data['transportation_budget'],
                  data['entertainment_budget'], data['other_budget']))
        
        db.commit()
        return jsonify({'message': 'Budget saved successfully'}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/weekly/history', methods=['GET'])
@login_required
@cross_origin()
def get_budget_history():
    """Get historical weekly budget data."""
    try:
        user_id = g.user['id']
        db = get_db()
        
        budgets = db.execute('''
            SELECT * FROM weekly_budgets 
            WHERE user_id = ? 
            ORDER BY week_start DESC 
            LIMIT 10
        ''', (user_id,)).fetchall()
        
        budget_history = []
        for budget in budgets:
            budget_history.append({
                'id': budget['id'],
                'week_start': budget['week_start'],
                'week_end': budget['week_end'],
                'total_budget': budget['total_budget'],
                'food_budget': budget['food_budget'],
                'transportation_budget': budget['transportation_budget'],
                'entertainment_budget': budget['entertainment_budget'],
                'other_budget': budget['other_budget']
            })
        
        return jsonify(budget_history)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500