from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class WeeklyBudget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)  
    amount = db.Column(db.Float, nullable=False)
    week_start_date = db.Column(db.Date, nullable=False)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class UserPoints(db.Model):
    __tablename__ = "user_points"
    user_id = db.Column(db.Integer, primary_key=True)
    total_points = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    current_streak = db.Column(db.Integer, default=0)

class Achievements(db.Model):
    __tablename__ = "achievements"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    icon = db.Column(db.String(255))

class UserAchievements(db.Model):
    __tablename__ = "user_achievements"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    achievement_id = db.Column(db.Integer)
    achieved_at = db.Column(db.DateTime, default=datetime.utcnow)

class Milestones(db.Model):
    __tablename__ = "milestones"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    condition_type = db.Column(db.String(50))
    condition_value = db.Column(db.Integer)
    reward_points = db.Column(db.Integer)
    reward_badge_id = db.Column(db.Integer)

class UserMilestones(db.Model):
    __tablename__ = "user_milestones"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    milestone_id = db.Column(db.Integer)
    is_completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)