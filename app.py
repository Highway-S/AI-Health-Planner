import os
import json
from datetime import datetime, date
from flask import Flask, render_template, request, jsonify, redirect, url_for
from models import db, User, HealthProfile, HealthRecord, MealPlan, MealItem, WorkoutPlan, WorkoutExercise, WeightHistory, AIRecommendation
import ai_engine

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'health-planner-secret-key-2026')

# Support Vercel serverless read-only filesystem by storing SQLite in /tmp
if os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
    db_uri = 'sqlite:////tmp/health_planner.db'
else:
    db_uri = 'sqlite:///health_planner.db'

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', db_uri)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"Database init notice: {e}")

def profile_to_dict(profile):
    return {
        'name': profile.user.name if profile.user else 'User',
        'age': profile.age or 25,
        'gender': profile.gender or 'male',
        'height': profile.height or 170.0,
        'weight': profile.weight or 70.0,
        'target_weight': profile.target_weight or 65.0,
        'goal': profile.goal or 'lose_weight',
        'timeline': profile.timeline or 3,
        'activity_level': profile.activity_level or 'moderate',
        'food_preferences': profile.food_preferences or '',
        'allergies': profile.allergies or '',
        'exercise_days': profile.exercise_days or 3,
        'equipment': profile.equipment or 'none',
        'fitness_level': profile.fitness_level or 'intermediate',
        'dietary_restrictions': profile.dietary_restrictions or ''
    }

def record_to_analysis(record):
    if not record:
        return None
    return {
        'bmi': {'value': record.bmi},
        'bmr': record.bmr,
        'tdee': record.tdee,
        'target_calories': record.target_calories,
        'macros': {
            'protein_g': record.protein_target,
            'carbs_g': record.carbs_target,
            'fat_g': record.fat_target
        },
        'water_intake': record.water_intake
    }

# ================= PAGE ROUTES =================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/app')
@app.route('/assessment')
def assessment():
    return render_template('app.html', section='assessment')

@app.route('/dashboard')
def dashboard_default():
    latest_user = User.query.order_by(User.id.desc()).first()
    if latest_user:
        return redirect(f'/dashboard/{latest_user.id}')
    return redirect('/assessment')

@app.route('/dashboard/<int:user_id>')
def dashboard(user_id):
    user = User.query.get(user_id)
    if not user:
        return redirect('/assessment')
    return render_template('app.html', section='dashboard', user_id=user_id)

# ================= API ROUTES =================

@app.route('/api/profile', methods=['POST'])
def create_profile():
    try:
        data = request.json or {}
        name = data.get('name', 'User')
        
        # Serialize list fields to comma-separated string if passed as list
        equipment = data.get('equipment', 'none')
        if isinstance(equipment, list):
            equipment = ', '.join(equipment) if equipment else 'none'
            
        food_prefs = data.get('food_preferences', '')
        if isinstance(food_prefs, list):
            food_prefs = ', '.join(food_prefs)
            
        allergies = data.get('allergies', '')
        if isinstance(allergies, list):
            allergies = ', '.join(allergies)

        user = User(name=name)
        db.session.add(user)
        db.session.flush()

        profile = HealthProfile(
            user_id=user.id,
            age=int(data.get('age', 25)),
            gender=data.get('gender', 'male'),
            height=float(data.get('height', 170)),
            weight=float(data.get('weight', 70)),
            target_weight=float(data.get('target_weight', 65)),
            goal=data.get('goal', 'lose_weight'),
            timeline=int(data.get('timeline', 3)),
            activity_level=data.get('activity_level', 'moderate'),
            food_preferences=food_prefs,
            allergies=allergies,
            exercise_days=int(data.get('exercise_days', 3)),
            equipment=equipment,
            fitness_level=data.get('fitness_level', 'intermediate'),
            dietary_restrictions=data.get('dietary_restrictions', '')
        )
        db.session.add(profile)
        
        weight_history = WeightHistory(
            user_id=user.id,
            weight=float(data.get('weight', 70)),
            date=date.today()
        )
        db.session.add(weight_history)
        
        db.session.commit()
        return jsonify({'success': True, 'user_id': user.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json or {}
        user_id = data.get('user_id')
        profile = HealthProfile.query.filter_by(user_id=user_id).first()
        if not profile:
            return jsonify({'success': False, 'error': 'Profile not found'}), 404
        
        profile_dict = profile_to_dict(profile)
        analysis_result = ai_engine.analyze_health(profile_dict)
        
        record = HealthRecord(
            user_id=user_id,
            bmi=analysis_result.get('bmi', {}).get('value'),
            bmr=analysis_result.get('bmr'),
            tdee=analysis_result.get('tdee'),
            target_calories=analysis_result.get('target_calories'),
            protein_target=analysis_result.get('macros', {}).get('protein_g'),
            carbs_target=analysis_result.get('macros', {}).get('carbs_g'),
            fat_target=analysis_result.get('macros', {}).get('fat_g'),
            water_intake=analysis_result.get('water_intake')
        )
        db.session.add(record)
        db.session.commit()
        
        return jsonify(analysis_result), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/meal-plan', methods=['POST'])
@app.route('/api/regenerate-meals', methods=['POST'])
def generate_meal_plan_route():
    try:
        data = request.json or {}
        user_id = data.get('user_id')
        profile = HealthProfile.query.filter_by(user_id=user_id).first()
        record = HealthRecord.query.filter_by(user_id=user_id).order_by(HealthRecord.created_at.desc()).first()
        
        if not profile:
            return jsonify({'success': False, 'error': 'Profile not found'}), 404
        
        profile_dict = profile_to_dict(profile)
        if record:
            analysis_dict = record_to_analysis(record)
        else:
            analysis_dict = ai_engine.analyze_health(profile_dict)
            
        meal_plan_data = ai_engine.generate_meal_plan(profile_dict, analysis_dict)
        
        meal_plan = MealPlan(user_id=user_id)
        db.session.add(meal_plan)
        db.session.flush()
        
        for meal in meal_plan_data.get('meals', []):
            item = MealItem(
                meal_plan_id=meal_plan.id,
                meal_type=meal.get('meal_type') or meal.get('type') or 'meal',
                food_name=meal.get('food_name') or meal.get('name'),
                food_name_th=meal.get('food_name_th') or meal.get('name_th'),
                portion=meal.get('portion_th') or meal.get('portion'),
                calories=meal.get('calories'),
                protein=meal.get('protein'),
                carbs=meal.get('carbs'),
                fat=meal.get('fat')
            )
            db.session.add(item)
            
        db.session.commit()
        return jsonify(meal_plan_data), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/workout-plan', methods=['POST'])
@app.route('/api/regenerate-workouts', methods=['POST'])
def generate_workout_plan_route():
    try:
        data = request.json or {}
        user_id = data.get('user_id')
        profile = HealthProfile.query.filter_by(user_id=user_id).first()
        record = HealthRecord.query.filter_by(user_id=user_id).order_by(HealthRecord.created_at.desc()).first()
        
        if not profile:
            return jsonify({'success': False, 'error': 'Profile not found'}), 404
            
        profile_dict = profile_to_dict(profile)
        if record:
            analysis_dict = record_to_analysis(record)
        else:
            analysis_dict = ai_engine.analyze_health(profile_dict)
            
        workout_plan_data = ai_engine.generate_workout_plan(profile_dict, analysis_dict)
        
        workout_plan = WorkoutPlan(user_id=user_id)
        db.session.add(workout_plan)
        db.session.flush()
        
        for workout in workout_plan_data.get('workouts', []):
            for ex in workout.get('exercises', []):
                item = WorkoutExercise(
                    workout_plan_id=workout_plan.id,
                    day=workout.get('day'),
                    day_th=workout.get('day_th'),
                    workout_type=workout.get('workout_type'),
                    exercise_name=ex.get('name'),
                    exercise_name_th=ex.get('name_th'),
                    sets=ex.get('sets'),
                    reps=str(ex.get('reps')) if ex.get('reps') is not None else None,
                    duration=str(ex.get('duration')) if ex.get('duration') is not None else None,
                    calories=ex.get('calories')
                )
                db.session.add(item)
            
        db.session.commit()
        return jsonify(workout_plan_data), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/progress', methods=['POST'])
def progress():
    try:
        data = request.json or {}
        user_id = data.get('user_id')
        weight = float(data.get('weight'))
        date_str = data.get('date') or date.today().strftime('%Y-%m-%d')
        
        record_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        weight_record = WeightHistory(user_id=user_id, weight=weight, date=record_date)
        db.session.add(weight_record)
        db.session.commit()
        
        profile = HealthProfile.query.filter_by(user_id=user_id).first()
        history = WeightHistory.query.filter_by(user_id=user_id).order_by(WeightHistory.date).all()
        
        history_list = [{'weight': h.weight, 'date': h.date.strftime('%Y-%m-%d')} for h in history]
        
        analysis = ai_engine.analyze_progress(history_list, profile.target_weight, profile.timeline, profile.goal)
        
        return jsonify({'success': True, 'history': history_list, 'analysis': analysis}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/ai-chat', methods=['POST'])
def ai_chat():
    try:
        data = request.json or {}
        user_id = data.get('user_id')
        message = data.get('message', '')
        
        profile = HealthProfile.query.filter_by(user_id=user_id).first()
        if not profile:
            profile_dict = {'name': 'คุณ', 'target_calories': 2000, 'goal': 'lose_weight'}
            analysis_dict = {'target_calories': 2000}
        else:
            profile_dict = profile_to_dict(profile)
            record = HealthRecord.query.filter_by(user_id=user_id).order_by(HealthRecord.created_at.desc()).first()
            if record:
                analysis_dict = record_to_analysis(record)
            else:
                analysis_dict = ai_engine.analyze_health(profile_dict)
                
        response = ai_engine.generate_chat_response(message, profile_dict, analysis_dict)
        
        if user_id:
            recommendation = AIRecommendation(
                user_id=user_id,
                recommendation_type='chat',
                content=json.dumps({'message': message, 'response': response}, ensure_ascii=False)
            )
            db.session.add(recommendation)
            db.session.commit()
            
        return jsonify({'response': response}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/dashboard/<int:user_id>')
def get_dashboard(user_id):
    try:
        profile = HealthProfile.query.filter_by(user_id=user_id).first()
        if not profile:
            return jsonify({'success': False, 'error': 'Profile not found'}), 404
            
        profile_dict = profile_to_dict(profile)
        analysis = ai_engine.analyze_health(profile_dict)
        meal_plan_data = ai_engine.generate_meal_plan(profile_dict, analysis)
        workout_plan_data = ai_engine.generate_workout_plan(profile_dict, analysis)
        
        history = WeightHistory.query.filter_by(user_id=user_id).order_by(WeightHistory.date).all()
        history_list = [{'weight': h.weight, 'date': h.date.strftime('%Y-%m-%d')} for h in history]
        
        progress_analysis = ai_engine.analyze_progress(history_list, profile.target_weight, profile.timeline, profile.goal)
        
        dashboard_data = {
            'profile': profile_dict,
            'analysis': analysis,
            'meal_plan': meal_plan_data,
            'workout_plan': workout_plan_data,
            'weight_history': history_list,
            'progress_analysis': progress_analysis
        }
            
        return jsonify(dashboard_data), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5050))
    print(f"🚀 AI Health Planner is running at: http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
