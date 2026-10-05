import os
import json
import logging
import secrets
from datetime import datetime, date
from flask import Flask, render_template, request, jsonify, redirect
from models import db, User, HealthProfile, HealthRecord, MealPlan, MealItem, WorkoutPlan, WorkoutExercise, WeightHistory, AIRecommendation
import ai_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
# Never ship a hard-coded secret; fall back to a random per-process key for local runs
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
app.config['MAX_CONTENT_LENGTH'] = 64 * 1024  # JSON payloads are tiny

# Support Vercel serverless read-only filesystem by storing SQLite in /tmp
if os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
    db_uri = 'sqlite:////tmp/health_planner.db'
else:
    os.makedirs(os.path.join(BASE_DIR, 'instance'), exist_ok=True)
    db_uri = 'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'health_planner.db')

database_url = os.environ.get('DATABASE_URL', db_uri)
# Heroku/Render style URLs use the deprecated postgres:// scheme
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    try:
        db.create_all()
    except Exception:
        logger.exception("Database init failed")

# ================= HELPERS =================

VALID_GENDERS = {'male', 'female'}
VALID_GOALS = {'lose_weight', 'gain_weight', 'maintain', 'build_muscle'}
VALID_ACTIVITY = {'sedentary', 'light', 'moderate', 'active', 'very_active'}
VALID_FITNESS = {'beginner', 'intermediate', 'advanced'}
VALID_EQUIPMENT = {'none', 'dumbbell', 'barbell', 'resistance_band', 'pull_up_bar', 'gym'}


class ValidationError(ValueError):
    """Raised for bad client input; returned to the client as a 400."""


def _json_body() -> dict:
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValidationError('Request body must be a JSON object')
    return data


def _number(data: dict, key: str, cast, lo, hi, default=None):
    raw = data.get(key)
    if raw is None or raw == '':
        if default is None:
            raise ValidationError(f'{key} is required')
        return default
    try:
        value = cast(float(raw))
    except (TypeError, ValueError):
        raise ValidationError(f'{key} must be a number')
    if not (lo <= value <= hi):
        raise ValidationError(f'{key} must be between {lo} and {hi}')
    return value


def _choice(data: dict, key: str, allowed: set, default: str) -> str:
    value = str(data.get(key) or default).strip().lower()
    if value not in allowed:
        raise ValidationError(f'{key} must be one of: {", ".join(sorted(allowed))}')
    return value


def _text(data: dict, key: str, max_len: int = 500) -> str:
    value = data.get(key) or ''
    if isinstance(value, list):
        value = ', '.join(str(v) for v in value)
    return str(value).strip()[:max_len]


def _user_id(data: dict) -> int:
    try:
        return int(data.get('user_id'))
    except (TypeError, ValueError):
        raise ValidationError('user_id is required')


def profile_to_dict(profile):
    return {
        'name': profile.user.name if profile.user else 'User',
        'age': profile.age or 25,
        'gender': profile.gender or 'male',
        'height': profile.height or 170.0,
        'weight': profile.weight or 70.0,
        'target_weight': profile.target_weight or profile.weight or 70.0,
        'goal': profile.goal or 'maintain',
        'timeline': profile.timeline or 3,
        'activity_level': profile.activity_level or 'moderate',
        'food_preferences': profile.food_preferences or '',
        'allergies': profile.allergies or '',
        'exercise_days': profile.exercise_days or 3,
        'equipment': profile.equipment or 'none',
        'fitness_level': profile.fitness_level or 'intermediate',
        'dietary_restrictions': profile.dietary_restrictions or ''
    }


def current_analysis(profile_dict: dict) -> dict:
    # Always recompute from the profile: stored HealthRecords miss fields
    # (bmi category, recommendations) and go stale after weight updates.
    return ai_engine.analyze_health(profile_dict)


def weight_history_list(user_id: int) -> list:
    history = (WeightHistory.query.filter_by(user_id=user_id)
               .order_by(WeightHistory.date, WeightHistory.id).all())
    return [{'weight': h.weight, 'date': h.date.strftime('%Y-%m-%d')} for h in history]


@app.errorhandler(ValidationError)
def handle_validation_error(e):
    db.session.rollback()
    return jsonify({'success': False, 'error': str(e)}), 400


@app.errorhandler(413)
def handle_too_large(e):
    return jsonify({'success': False, 'error': 'Request too large'}), 413


@app.errorhandler(Exception)
def handle_unexpected_error(e):
    from werkzeug.exceptions import HTTPException
    if isinstance(e, HTTPException):
        return e
    db.session.rollback()
    # Log details server-side; never leak internals to the client
    logger.exception("Unhandled error")
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

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
    # Don't expose another person's dashboard: the client remembers its own user id
    return render_template('app.html', section='dashboard_resume')


@app.route('/dashboard/<int:user_id>')
def dashboard(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return redirect('/assessment')
    return render_template('app.html', section='dashboard', user_id=user_id)


@app.route('/healthz')
def healthz():
    return jsonify({'status': 'ok'}), 200

# ================= API ROUTES =================

@app.route('/api/profile', methods=['POST'])
def create_profile():
    data = _json_body()
    name = _text(data, 'name', 100)
    if not name:
        raise ValidationError('name is required')

    weight = _number(data, 'weight', float, 20, 400)
    equipment_raw = data.get('equipment') or 'none'
    if isinstance(equipment_raw, str):
        equipment_raw = equipment_raw.split(',')
    equipment = [e.strip().lower() for e in equipment_raw if str(e).strip()]
    equipment = [e for e in equipment if e in VALID_EQUIPMENT] or ['none']

    user = User(name=name)
    db.session.add(user)
    db.session.flush()

    profile = HealthProfile(
        user_id=user.id,
        age=_number(data, 'age', int, 10, 120),
        gender=_choice(data, 'gender', VALID_GENDERS, 'male'),
        height=_number(data, 'height', float, 80, 250),
        weight=weight,
        target_weight=_number(data, 'target_weight', float, 20, 400, default=weight),
        goal=_choice(data, 'goal', VALID_GOALS, 'maintain'),
        timeline=_number(data, 'timeline', int, 1, 36, default=3),
        activity_level=_choice(data, 'activity_level', VALID_ACTIVITY, 'moderate'),
        food_preferences=_text(data, 'food_preferences'),
        allergies=_text(data, 'allergies'),
        exercise_days=_number(data, 'exercise_days', int, 1, 7, default=3),
        equipment=', '.join(equipment),
        fitness_level=_choice(data, 'fitness_level', VALID_FITNESS, 'beginner'),
        dietary_restrictions=_text(data, 'dietary_restrictions')
    )
    db.session.add(profile)
    db.session.add(WeightHistory(user_id=user.id, weight=weight, date=date.today()))
    db.session.commit()
    return jsonify({'success': True, 'user_id': user.id}), 201

def _load_profile(user_id: int):
    profile = HealthProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        return None, (jsonify({'success': False, 'error': 'Profile not found'}), 404)
    return profile, None


def _save_meal_plan(user_id: int, meal_plan_data: dict):
    meal_plan = MealPlan(user_id=user_id, date=date.today())
    db.session.add(meal_plan)
    db.session.flush()
    for meal in meal_plan_data.get('meals', []):
        db.session.add(MealItem(
            meal_plan_id=meal_plan.id,
            meal_type=meal['meal_type'],
            food_name=meal['food_name'],
            food_name_th=meal['food_name_th'],
            portion=meal['portion_th'],
            calories=meal['calories'],
            protein=meal['protein'],
            carbs=meal['carbs'],
            fat=meal['fat']
        ))


def _save_workout_plan(user_id: int, workout_plan_data: dict):
    workout_plan = WorkoutPlan(user_id=user_id)
    db.session.add(workout_plan)
    db.session.flush()
    for workout in workout_plan_data.get('workouts', []):
        for ex in workout.get('exercises', []):
            db.session.add(WorkoutExercise(
                workout_plan_id=workout_plan.id,
                day=workout.get('day'),
                day_th=workout.get('day_th'),
                workout_type=workout.get('workout_type'),
                exercise_name=ex.get('name'),
                exercise_name_th=ex.get('name_th'),
                sets=ex.get('sets'),
                reps=str(ex['reps']) if ex.get('reps') is not None else None,
                duration=str(ex['duration']) if ex.get('duration') is not None else None,
                calories=ex.get('calories')
            ))


@app.route('/api/analyze', methods=['POST'])
def analyze():
    user_id = _user_id(_json_body())
    profile, err = _load_profile(user_id)
    if err:
        return err

    analysis_result = current_analysis(profile_to_dict(profile))
    db.session.add(HealthRecord(
        user_id=user_id,
        bmi=analysis_result['bmi']['value'],
        bmr=analysis_result['bmr'],
        tdee=analysis_result['tdee'],
        target_calories=analysis_result['target_calories'],
        protein_target=analysis_result['macros']['protein_g'],
        carbs_target=analysis_result['macros']['carbs_g'],
        fat_target=analysis_result['macros']['fat_g'],
        water_intake=analysis_result['water_intake']
    ))
    db.session.commit()
    return jsonify(analysis_result), 200


@app.route('/api/meal-plan', methods=['POST'])
@app.route('/api/regenerate-meals', methods=['POST'])
def generate_meal_plan_route():
    user_id = _user_id(_json_body())
    profile, err = _load_profile(user_id)
    if err:
        return err

    profile_dict = profile_to_dict(profile)
    # /api/meal-plan is the stable "today" plan; regenerate gives a fresh random one
    seed = None if request.path.endswith('regenerate-meals') else ai_engine.daily_seed(user_id, 'meals')
    meal_plan_data = ai_engine.generate_meal_plan(profile_dict, current_analysis(profile_dict), seed=seed)
    _save_meal_plan(user_id, meal_plan_data)
    db.session.commit()
    return jsonify(meal_plan_data), 200


@app.route('/api/workout-plan', methods=['POST'])
@app.route('/api/regenerate-workouts', methods=['POST'])
def generate_workout_plan_route():
    user_id = _user_id(_json_body())
    profile, err = _load_profile(user_id)
    if err:
        return err

    profile_dict = profile_to_dict(profile)
    seed = None if request.path.endswith('regenerate-workouts') else ai_engine.daily_seed(user_id, 'workout')
    workout_plan_data = ai_engine.generate_workout_plan(profile_dict, current_analysis(profile_dict), seed=seed)
    _save_workout_plan(user_id, workout_plan_data)
    db.session.commit()
    return jsonify(workout_plan_data), 200

@app.route('/api/progress', methods=['POST'])
def progress():
    data = _json_body()
    user_id = _user_id(data)
    profile, err = _load_profile(user_id)
    if err:
        return err

    weight = _number(data, 'weight', float, 20, 400)
    date_str = data.get('date') or date.today().strftime('%Y-%m-%d')
    try:
        record_date = datetime.strptime(str(date_str), '%Y-%m-%d').date()
    except ValueError:
        raise ValidationError('date must be YYYY-MM-DD')
    if record_date > date.today():
        raise ValidationError('date cannot be in the future')

    # One entry per day: logging again on the same date updates it
    existing = WeightHistory.query.filter_by(user_id=user_id, date=record_date).first()
    if existing:
        existing.weight = weight
    else:
        db.session.add(WeightHistory(user_id=user_id, weight=weight, date=record_date))

    # Keep the profile's current weight in sync with the latest entry so
    # BMI / calorie targets follow real progress
    latest = (WeightHistory.query.filter_by(user_id=user_id)
              .order_by(WeightHistory.date.desc(), WeightHistory.id.desc()).first())
    if latest is None or record_date >= latest.date:
        profile.weight = weight
    db.session.commit()

    history_list = weight_history_list(user_id)
    analysis = ai_engine.analyze_progress(history_list, profile.target_weight, profile.timeline, profile.goal)
    return jsonify({'success': True, 'history': history_list, 'analysis': analysis}), 200


@app.route('/api/ai-chat', methods=['POST'])
def ai_chat():
    data = _json_body()
    message = _text(data, 'message', 1000)
    if not message:
        raise ValidationError('message is required')
    lang = data.get('lang') if data.get('lang') in ('th', 'en') else None

    user_id = None
    profile = None
    if data.get('user_id') not in (None, ''):
        user_id = _user_id(data)
        profile = HealthProfile.query.filter_by(user_id=user_id).first()

    if not profile:
        profile_dict = {'name': '', 'goal': 'maintain'}
        analysis_dict = {'target_calories': 2000}
    else:
        profile_dict = profile_to_dict(profile)
        analysis_dict = current_analysis(profile_dict)

    response = ai_engine.generate_chat_response(message, profile_dict, analysis_dict, lang=lang)

    if profile:
        db.session.add(AIRecommendation(
            user_id=user_id,
            recommendation_type='chat',
            content=json.dumps({'message': message, 'response': response}, ensure_ascii=False)
        ))
        db.session.commit()

    return jsonify({'response': response}), 200


@app.route('/api/dashboard/<int:user_id>')
def get_dashboard(user_id):
    profile, err = _load_profile(user_id)
    if err:
        return err

    profile_dict = profile_to_dict(profile)
    analysis = current_analysis(profile_dict)
    meal_plan_data = ai_engine.generate_meal_plan(profile_dict, analysis, seed=ai_engine.daily_seed(user_id, 'meals'))
    workout_plan_data = ai_engine.generate_workout_plan(profile_dict, analysis, seed=ai_engine.daily_seed(user_id, 'workout'))
    history_list = weight_history_list(user_id)
    progress_analysis = ai_engine.analyze_progress(history_list, profile.target_weight, profile.timeline, profile.goal)

    return jsonify({
        'success': True,
        'user_id': user_id,
        'profile': profile_dict,
        'analysis': analysis,
        'meal_plan': meal_plan_data,
        'workout_plan': workout_plan_data,
        'weight_history': history_list,
        'progress_analysis': progress_analysis
    }), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5050))
    print(f"🚀 AI Health Planner is running at: http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('FLASK_DEBUG') == '1')
