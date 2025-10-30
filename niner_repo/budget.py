from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, g
from flask_cors import cross_origin
from datetime import datetime, timedelta
from auth import login_required
from db import get_db
import sqlite3

bp = Blueprint('budget', __name__, url_prefix='/budget')

@bp.route('/')
@login_required
def index():
    """Main budget planning page"""
    try:
        user_id = g.user['id']
        db = get_db()
        
        # Get current week's start and end dates
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        # Get current weekly budget
        current_budget = db.execute('''
            SELECT * FROM weekly_budgets 
            WHERE user_id = ? AND week_start = ?
        ''', (user_id, start_of_week.strftime('%Y-%m-%d'))).fetchone()
        
        # Get expenses for this week
        expenses = db.execute('''
            SELECT category, SUM(amount) as total_spent
            FROM transactions 
            WHERE user_id = ? AND type = 'expense' AND date BETWEEN ? AND ?
            GROUP BY category
        ''', (user_id, start_of_week.strftime('%Y-%m-%d'), end_of_week.strftime('%Y-%m-%d'))).fetchall()
        
        expenses_dict = {expense['category']: float(expense['total_spent']) for expense in expenses}
        
        # Get total income for budget suggestions
        total_income = db.execute('''
            SELECT SUM(amount) as total
            FROM income 
            WHERE user_id = ? AND is_active = 1
        ''', (user_id,)).fetchone()
        
        monthly_income = float(total_income['total']) if total_income and total_income['total'] else 0
        
        # Get recent spending patterns for suggestions
        recent_expenses = db.execute('''
            SELECT category, AVG(amount) as avg_amount, COUNT(*) as frequency
            FROM transactions 
            WHERE user_id = ? AND type = 'expense' AND date >= date('now', '-30 days')
            GROUP BY category
        ''', (user_id,)).fetchall()
        
        spending_patterns = {expense['category']: {
            'avg_amount': float(expense['avg_amount']),
            'frequency': expense['frequency']
        } for expense in recent_expenses}
        
        return render_template('home/budget.html', 
                             current_budget=current_budget,
                             expenses=expenses_dict,
                             monthly_income=monthly_income,
                             spending_patterns=spending_patterns,
                             week_start=start_of_week.strftime('%Y-%m-%d'),
                             week_end=end_of_week.strftime('%Y-%m-%d'))
        
    except Exception as e:
        flash(f'Error loading budget data: {str(e)}', 'error')
        return render_template('home/budget.html', 
                             current_budget=None,
                             expenses={},
                             monthly_income=0,
                             spending_patterns={})

@bp.route('/create')
@login_required
def create():
    return render_template('home/budget.html')