import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_DB_FD, _DB_PATH = tempfile.mkstemp(suffix='.db')
os.close(_DB_FD)
os.environ['DATABASE_URL'] = f'sqlite:///{_DB_PATH}'

import ai_engine  # noqa: E402
from app import app  # noqa: E402

PROFILE = {
    'name': 'Test User', 'age': 30, 'gender': 'male', 'height': 175, 'weight': 80,
    'target_weight': 72, 'goal': 'lose_weight', 'timeline': 3, 'activity_level': 'moderate',
    'exercise_days': 3, 'fitness_level': 'beginner', 'equipment': ['none'],
}


class EngineTests(unittest.TestCase):
    def test_allergy_filter_excludes_seafood(self):
        foods = ai_engine.filter_foods({'allergies': 'อาหารทะเล, กุ้ง'})
        self.assertTrue(foods)
        self.assertFalse([f['name'] for f in foods if 'seafood' in f['allergens']])

    def test_vegetarian_has_no_meat(self):
        foods = ai_engine.filter_foods({'dietary_restrictions': 'vegetarian'})
        for f in foods:
            self.assertNotRegex(f['name'], r'Chicken|Pork|Beef|Shrimp|Fish|Squid')

    def test_gain_goal_with_lower_target_has_no_negative_surplus(self):
        res = ai_engine.calculate_target_calories(2000, 'gain_weight', 70, 65, 3)
        self.assertGreaterEqual(res['target_calories'], 2000)

    def test_zero_timeline_does_not_crash(self):
        ai_engine.calculate_target_calories(2000, 'lose_weight', 80, 70, 0)

    def test_plans_are_deterministic_for_seed(self):
        a = ai_engine.analyze_health(PROFILE)
        p1 = ai_engine.generate_meal_plan(PROFILE, a, seed=42)
        p2 = ai_engine.generate_meal_plan(PROFILE, a, seed=42)
        self.assertEqual([m['food_name'] for m in p1['meals']], [m['food_name'] for m in p2['meals']])

    def test_workout_respects_days(self):
        a = ai_engine.analyze_health(PROFILE)
        plan = ai_engine.generate_workout_plan(PROFILE, a, seed=1)
        self.assertEqual(sum(1 for d in plan['workouts'] if not d['is_rest']), 3)


class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()
        res = cls.client.post('/api/profile', json=PROFILE)
        assert res.status_code == 201, res.json
        cls.uid = res.json['user_id']

    def test_endpoints_ok(self):
        for path in ['/api/analyze', '/api/meal-plan', '/api/workout-plan',
                     '/api/regenerate-meals', '/api/regenerate-workouts']:
            self.assertEqual(self.client.post(path, json={'user_id': self.uid}).status_code, 200, path)
        self.assertEqual(self.client.get(f'/api/dashboard/{self.uid}').status_code, 200)

    def test_validation_errors(self):
        self.assertEqual(self.client.post('/api/profile', json={'age': 'abc'}).status_code, 400)
        self.assertEqual(self.client.post('/api/analyze', json={'user_id': 99999}).status_code, 404)
        self.assertEqual(self.client.post('/api/analyze', json={}).status_code, 400)

    def test_progress_rejects_future_date(self):
        res = self.client.post('/api/progress', json={'user_id': self.uid, 'weight': 79, 'date': '2999-01-01'})
        self.assertEqual(res.status_code, 400)

    def test_progress_logs_weight(self):
        res = self.client.post('/api/progress', json={'user_id': self.uid, 'weight': 79.5})
        self.assertEqual(res.status_code, 200)
        self.assertIn('analysis', res.json)

    def test_unknown_dashboard_page_renders_for_local_fallback(self):
        # The page loads so the client can fall back to its localStorage copy
        self.assertEqual(self.client.get('/dashboard/99999').status_code, 200)

    def test_endpoints_use_client_profile_when_db_row_missing(self):
        body = {'user_id': 99999, 'profile': {**PROFILE, 'equipment': 'machine, barbell'}}
        for path in ['/api/analyze', '/api/meal-plan', '/api/workout-plan',
                     '/api/regenerate-meals', '/api/regenerate-workouts']:
            self.assertEqual(self.client.post(path, json=body).status_code, 200, path)

    def test_progress_with_client_history_when_db_row_missing(self):
        res = self.client.post('/api/progress', json={
            'user_id': 99999, 'profile': PROFILE, 'weight': 79, 'date': '2024-01-02',
            'history': [{'date': '2024-01-01', 'weight': 80}, {'date': 'bad', 'weight': 1}],
        })
        self.assertEqual(res.status_code, 200)
        self.assertEqual([h['date'] for h in res.json['history']], ['2024-01-01', '2024-01-02'])

    def test_invalid_client_profile_rejected(self):
        res = self.client.post('/api/analyze', json={'user_id': 99999, 'profile': {'age': 'abc'}})
        self.assertEqual(res.status_code, 400)


def tearDownModule():
    try:
        os.remove(_DB_PATH)
    except OSError:
        pass


if __name__ == '__main__':
    unittest.main()
