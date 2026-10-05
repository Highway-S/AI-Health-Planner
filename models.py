from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # relationships
    health_profile = db.relationship('HealthProfile', backref='user', uselist=False, lazy=True)
    weight_history = db.relationship('WeightHistory', backref='user', lazy=True, order_by='WeightHistory.date')
    meal_plans = db.relationship('MealPlan', backref='user', lazy=True)
    workout_plans = db.relationship('WorkoutPlan', backref='user', lazy=True)
    ai_recommendations = db.relationship('AIRecommendation', backref='user', lazy=True)

class HealthProfile(db.Model):
    __tablename__ = 'health_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    height = db.Column(db.Float)  # cm
    weight = db.Column(db.Float)  # kg
    target_weight = db.Column(db.Float)
    goal = db.Column(db.String(50))  # lose_weight, gain_weight, maintain, build_muscle
    timeline = db.Column(db.Integer)  # months
    activity_level = db.Column(db.String(20))  # sedentary, light, moderate, active, very_active
    food_preferences = db.Column(db.Text)  # comma-separated
    allergies = db.Column(db.Text)  # comma-separated
    exercise_days = db.Column(db.Integer)  # days per week
    equipment = db.Column(db.Text)  # comma-separated
    fitness_level = db.Column(db.String(20))  # beginner, intermediate, advanced
    dietary_restrictions = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class HealthRecord(db.Model):
    __tablename__ = 'health_records'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    bmi = db.Column(db.Float)
    bmr = db.Column(db.Float)
    tdee = db.Column(db.Float)
    target_calories = db.Column(db.Float)
    protein_target = db.Column(db.Float)
    carbs_target = db.Column(db.Float)
    fat_target = db.Column(db.Float)
    water_intake = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class MealPlan(db.Model):
    __tablename__ = 'meal_plans'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('MealItem', backref='meal_plan', lazy=True)

class MealItem(db.Model):
    __tablename__ = 'meal_items'
    id = db.Column(db.Integer, primary_key=True)
    meal_plan_id = db.Column(db.Integer, db.ForeignKey('meal_plans.id'), nullable=False)
    meal_type = db.Column(db.String(20))  # breakfast, lunch, dinner, snack
    food_name = db.Column(db.String(200))
    food_name_th = db.Column(db.String(200))
    portion = db.Column(db.String(100))
    calories = db.Column(db.Float)
    protein = db.Column(db.Float)
    carbs = db.Column(db.Float)
    fat = db.Column(db.Float)

class WorkoutPlan(db.Model):
    __tablename__ = 'workout_plans'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    exercises = db.relationship('WorkoutExercise', backref='workout_plan', lazy=True)

class WorkoutExercise(db.Model):
    __tablename__ = 'workout_exercises'
    id = db.Column(db.Integer, primary_key=True)
    workout_plan_id = db.Column(db.Integer, db.ForeignKey('workout_plans.id'), nullable=False)
    day = db.Column(db.String(20))
    day_th = db.Column(db.String(20))
    workout_type = db.Column(db.String(50))
    exercise_name = db.Column(db.String(200))
    exercise_name_th = db.Column(db.String(200))
    sets = db.Column(db.Integer, nullable=True)
    reps = db.Column(db.String(20), nullable=True)
    duration = db.Column(db.String(50), nullable=True)
    calories = db.Column(db.Float)

class WeightHistory(db.Model):
    __tablename__ = 'weight_history'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    weight = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AIRecommendation(db.Model):
    __tablename__ = 'ai_recommendations'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recommendation_type = db.Column(db.String(50))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
