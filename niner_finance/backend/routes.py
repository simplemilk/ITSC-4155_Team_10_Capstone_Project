from flask import Blueprint, request, jsonify
from models import db, WeeklyBudget, UserPoints, UserMilestone, Milestone
from datetime import datetime, timedelta
import re


budget_bp = Blueprint('budget', __name__)

@budget_bp.route('/api/budget/<int:user_id>', methods=['GET'])
def get_weekly_budget(user_id):
    budget = WeeklyBudget.query.filter_by(user_id=user_id).first()

    if budget:
        return jsonify({
            'budget': {
                'amount': budget.amount,
                'income': 2500,  # Example income
                'expenses': 1000,  # Example expenses
                'savings': 1500  # Example savings
            }
        }), 200
    else:
        return jsonify({'error': 'Budget not found'}), 404


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

def award_points(user_id, amount):
    user = UserPoints.query.get(user_id)

    if not user:
        user = UserPoints(user_id=user_id)
        db.session.add(user)

    user.total_points += amount

    # Level calculation
    if user.total_points >= 1000:
        user.level = 5
    elif user.total_points >= 500:
        user.level = 4
    elif user.total_points >= 250:
        user.level = 3
    elif user.total_points >= 100:
        user.level = 2
    else:
        user.level = 1

    db.session.commit()

def update_streak(user_id):
    user = UserPoints.query.get(user_id)

    now = datetime.utcnow()
    if not user.last_login:
        user.current_streak = 1
    else:
        if (now - user.last_login) <= timedelta(hours=48):
            user.current_streak += 1
        else:
            user.current_streak = 1

    user.last_login = now
    db.session.commit()

def check_milestones(user_id, triggered_action):
    milestones = Milestone.query.all()

    for m in milestones:
        already_done = UserMilestone.query.filter_by(
            user_id=user_id,
            milestone_id=m.id,
            is_completed=True
        ).first()

        if already_done:
            continue

        if m.condition_type == triggered_action:
            award_points(user_id, m.reward_points)

            entry = UserMilestone(
                user_id=user_id,
                milestone_id=m.id,
                is_completed=True,
                completed_at=datetime.utcnow()
            )
            db.session.add(entry)
            db.session.commit()

@budget_bp.route("/api/game/user/<int:user_id>", methods=["GET"])
def get_user_game_data(user_id):
    user = UserPoints.query.get(user_id)

    if not user:
        user = UserPoints(user_id=user_id)
        db.session.add(user)
        db.session.commit()

    # Update daily streak on each visit
    update_streak(user_id)

    return jsonify({
        "user_id": user_id,
        "points": user.total_points,
        "level": user.level,
        "current_streak": user.current_streak
    })


@budget_bp.route("/api/game/complete-budget", methods=["POST"])
def complete_budget_reward():
    data = request.json
    user_id = data.get("user_id", 1)

    award_points(user_id, 20)

    check_milestones(user_id, "budget_completed")

    return jsonify({"message": "Budget completion rewarded!"})