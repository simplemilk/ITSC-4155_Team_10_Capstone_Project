<<<<<<< HEAD
from flask import Blueprint, request, jsonify
from models import db, WeeklyBudget
from datetime import datetime
import re

budget_bp = Blueprint('budget', __name__)

@budget_bp.route('/api/budget', methods=['POST'])
def set_weekly_budget():
    data = request.json
    user_id = data.get('user_id')
    amount = data.get('amount')
    week_start = data.get('week_start_date')

    if not user_id or not amount or not week_start:
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({'error': 'Amount must be positive'}), 400

        # Validate date format YYYY-MM-DD
        if not re.match(r'\d{4}-\d{2}-\d{2}', week_start):
            return jsonify({'error': 'Invalid date format'}), 400

        week_start_date = datetime.strptime(week_start, '%Y-%m-%d').date()

    except Exception as e:
        return jsonify({'error': 'Invalid input data'}), 400

    # Check if budget for that week/user already exists
    budget = WeeklyBudget.query.filter_by(user_id=user_id, week_start_date=week_start_date).first()

    if budget:
        budget.amount = amount
    else:
        budget = WeeklyBudget(user_id=user_id, amount=amount, week_start_date=week_start_date)
        db.session.add(budget)

    db.session.commit()

    return jsonify({'message': 'Budget set successfully', 'budget': {
        'user_id': user_id,
        'amount': amount,
        'week_start_date': week_start
    }}), 200
=======
from flask import Blueprint, request, jsonify
from models import db, WeeklyBudget
from datetime import datetime
import re

budget_bp = Blueprint('budget', __name__)

@budget_bp.route('/api/budget', methods=['POST'])
def set_weekly_budget():
    data = request.json
    user_id = data.get('user_id')
    amount = data.get('amount')
    week_start = data.get('week_start_date')

    if not user_id or not amount or not week_start:
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({'error': 'Amount must be positive'}), 400

        # Validate date format YYYY-MM-DD
        if not re.match(r'\d{4}-\d{2}-\d{2}', week_start):
            return jsonify({'error': 'Invalid date format'}), 400

        week_start_date = datetime.strptime(week_start, '%Y-%m-%d').date()

    except Exception as e:
        return jsonify({'error': 'Invalid input data'}), 400

    # Check if budget for that week/user already exists
    budget = WeeklyBudget.query.filter_by(user_id=user_id, week_start_date=week_start_date).first()

    if budget:
        budget.amount = amount
    else:
        budget = WeeklyBudget(user_id=user_id, amount=amount, week_start_date=week_start_date)
        db.session.add(budget)

    db.session.commit()

    return jsonify({'message': 'Budget set successfully', 'budget': {
        'user_id': user_id,
        'amount': amount,
        'week_start_date': week_start
    }}), 200
>>>>>>> c663b277920c15a2a6b669ad40363a728377b600
