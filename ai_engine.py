import random
import math
import hashlib
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

# ==========================================
# 1. Core Health Calculations
# ==========================================

def calculate_bmi(weight_kg: float, height_cm: float) -> dict:
    """Calculate BMI and return dictionary with category and descriptions."""
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2) if height_m > 0 else 0
    
    if bmi < 18.5:
        return {'value': bmi, 'category': 'น้ำหนักน้อย', 'description': 'คุณมีน้ำหนักต่ำกว่าเกณฑ์ปกติ ควรเพิ่มน้ำหนักและมวลกล้ามเนื้อ', 'color': 'blue'}
    elif bmi < 25:
        return {'value': bmi, 'category': 'น้ำหนักปกติ', 'description': 'คุณมีน้ำหนักอยู่ในเกณฑ์มาตรฐาน ควรรักษาสุขภาพและออกกำลังกายสม่ำเสมอ', 'color': 'green'}
    elif bmi < 30:
        return {'value': bmi, 'category': 'น้ำหนักเกิน', 'description': 'คุณมีน้ำหนักเกินมาตรฐาน ควรเริ่มควบคุมอาหารและออกกำลังกาย', 'color': 'orange'}
    else:
        return {'value': bmi, 'category': 'อ้วน', 'description': 'คุณอยู่ในเกณฑ์โรคอ้วน ควรปรึกษาแพทย์และปรับพฤติกรรมอย่างจริงจัง', 'color': 'red'}

def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    """Calculate Basal Metabolic Rate using Mifflin-St Jeor equation."""
    base = 10 * weight_kg + 6.25 * height_cm - 5 * age
    if gender.lower() in ['male', 'm', 'ชาย']:
        return base + 5
    else:
        return base - 161

def calculate_tdee(bmr: float, activity_level: str) -> float:
    """Calculate Total Daily Energy Expenditure."""
    multipliers = {
        'sedentary': 1.2,
        'light': 1.375,
        'moderate': 1.55,
        'active': 1.725,
        'very_active': 1.9
    }
    return bmr * multipliers.get(activity_level.lower(), 1.2)

def calculate_target_calories(tdee: float, goal: str, weight_kg: float, target_weight_kg: float, timeline_months: int) -> dict:
    """Calculate daily target calories based on goal and timeline."""
    goal = goal.lower()
    
    if goal == 'lose_weight':
        weight_diff = weight_kg - target_weight_kg
        total_cal_deficit_needed = weight_diff * 7700
        days = timeline_months * 30
        daily_deficit = total_cal_deficit_needed / days if days > 0 else 500
        daily_deficit = min(daily_deficit, 1000.0) # Safe limit max 1000 kcal deficit
        target = tdee - daily_deficit
        return {
            'target_calories': target,
            'deficit_or_surplus': -daily_deficit,
            'weekly_change_kg': (daily_deficit * 7) / 7700
        }
    elif goal == 'gain_weight' or goal == 'build_muscle':
        weight_diff = target_weight_kg - weight_kg
        total_cal_surplus_needed = weight_diff * 7700
        days = timeline_months * 30
        daily_surplus = total_cal_surplus_needed / days if days > 0 else 300
        daily_surplus = min(daily_surplus, 500.0) # Safe limit max 500 kcal surplus
        target = tdee + daily_surplus
        return {
            'target_calories': target,
            'deficit_or_surplus': daily_surplus,
            'weekly_change_kg': (daily_surplus * 7) / 7700
        }
    else: # maintain
        return {
            'target_calories': tdee,
            'deficit_or_surplus': 0.0,
            'weekly_change_kg': 0.0
        }

def calculate_macros(target_calories: float, weight_kg: float, goal: str) -> dict:
    """Calculate recommended daily macronutrients."""
    goal = goal.lower()
    if goal == 'lose_weight':
        protein_per_kg = 2.0
    elif goal == 'gain_weight':
        protein_per_kg = 1.8
    elif goal == 'build_muscle':
        protein_per_kg = 2.2
    else:
        protein_per_kg = 1.5
        
    protein_g = weight_kg * protein_per_kg
    protein_cal = protein_g * 4
    
    fat_cal = target_calories * 0.25
    fat_g = fat_cal / 9
    
    carbs_cal = target_calories - protein_cal - fat_cal
    carbs_g = carbs_cal / 4
    
    return {
        'protein_g': protein_g, 'protein_cal': protein_cal,
        'carbs_g': carbs_g, 'carbs_cal': carbs_cal,
        'fat_g': fat_g, 'fat_cal': fat_cal
    }

def calculate_water_intake(weight_kg: float, activity_level: str) -> float:
    """Calculate recommended daily water intake in liters."""
    base = weight_kg * 0.033
    if activity_level.lower() in ['active', 'very_active']:
        base += 0.5
    return round(base, 1)

# ==========================================
# 2. Comprehensive Databases
# ==========================================

def _generate_thai_food_db() -> List[Dict]:
    """Generates a database of 80+ Thai food items."""
    db = []
    meats = [('Chicken', 'ไก่', 150, 20, 2, 'high_protein'), ('Pork', 'หมู', 200, 18, 10, 'keto'), 
             ('Beef', 'เนื้อ', 220, 22, 12, 'high_protein'), ('Shrimp', 'กุ้ง', 120, 18, 1, 'low_fat'), 
             ('Tofu', 'เต้าหู้', 140, 12, 8, 'vegetarian,vegan')]
    
    # 1. Stir-fries (25 items)
    for en_meat, th_meat, c, p, f, tag in meats:
        db.append({'name': f'Basil {en_meat}', 'name_th': f'ผัดกะเพรา{th_meat}', 'category': 'stir_fry', 'meal_types': ['lunch', 'dinner'], 'calories': c+150, 'protein': p, 'carbs': 5, 'fat': f+10, 'portion': '1 plate', 'portion_th': '1 จาน', 'tags': [tag], 'allergens': ['soy']})
        db.append({'name': f'Garlic {en_meat}', 'name_th': f'{th_meat}ทอดกระเทียม', 'category': 'stir_fry', 'meal_types': ['lunch', 'dinner'], 'calories': c+180, 'protein': p, 'carbs': 8, 'fat': f+12, 'portion': '1 plate', 'portion_th': '1 จาน', 'tags': [tag], 'allergens': ['soy', 'gluten']})
        db.append({'name': f'{en_meat} Fried Rice', 'name_th': f'ข้าวผัด{th_meat}', 'category': 'rice', 'meal_types': ['breakfast', 'lunch', 'dinner'], 'calories': c+250, 'protein': p+5, 'carbs': 45, 'fat': f+10, 'portion': '1 plate', 'portion_th': '1 จาน', 'tags': [], 'allergens': ['eggs', 'soy']})
        db.append({'name': f'Pad Thai with {en_meat}', 'name_th': f'ผัดไทย{th_meat}', 'category': 'noodle', 'meal_types': ['lunch', 'dinner'], 'calories': c+300, 'protein': p+6, 'carbs': 50, 'fat': f+15, 'portion': '1 plate', 'portion_th': '1 จาน', 'tags': [], 'allergens': ['eggs', 'nuts', 'soy']})
        db.append({'name': f'Pad See Ew {en_meat}', 'name_th': f'ผัดซีอิ๊ว{th_meat}', 'category': 'noodle', 'meal_types': ['lunch', 'dinner'], 'calories': c+280, 'protein': p+5, 'carbs': 40, 'fat': f+12, 'portion': '1 plate', 'portion_th': '1 จาน', 'tags': [], 'allergens': ['eggs', 'soy', 'gluten']})

    # 2. Soups & Curries (20 items)
    for en_meat, th_meat, c, p, f, tag in meats[:4]: 
        db.append({'name': f'Tom Yum {en_meat}', 'name_th': f'ต้มยำ{th_meat}', 'category': 'soup', 'meal_types': ['lunch', 'dinner'], 'calories': c+50, 'protein': p, 'carbs': 8, 'fat': f+2, 'portion': '1 bowl', 'portion_th': '1 ชาม', 'tags': ['low_carb', tag], 'allergens': ['seafood'] if en_meat=='Shrimp' else []})
        db.append({'name': f'Green Curry {en_meat}', 'name_th': f'แกงเขียวหวาน{th_meat}', 'category': 'curry', 'meal_types': ['lunch', 'dinner'], 'calories': c+200, 'protein': p, 'carbs': 12, 'fat': f+18, 'portion': '1 bowl', 'portion_th': '1 ชาม', 'tags': ['keto'], 'allergens': []})
        db.append({'name': f'Panang Curry {en_meat}', 'name_th': f'พะแนง{th_meat}', 'category': 'curry', 'meal_types': ['lunch', 'dinner'], 'calories': c+220, 'protein': p, 'carbs': 15, 'fat': f+20, 'portion': '1 bowl', 'portion_th': '1 ชาม', 'tags': [], 'allergens': ['nuts']})
        db.append({'name': f'Clear Soup {en_meat}', 'name_th': f'แกงจืด{th_meat}', 'category': 'soup', 'meal_types': ['breakfast', 'lunch', 'dinner'], 'calories': c+30, 'protein': p, 'carbs': 5, 'fat': f, 'portion': '1 bowl', 'portion_th': '1 ชาม', 'tags': ['low_fat', 'low_carb'], 'allergens': ['soy']})
        db.append({'name': f'Massaman Curry {en_meat}', 'name_th': f'แกงมัสมั่น{th_meat}', 'category': 'curry', 'meal_types': ['lunch', 'dinner'], 'calories': c+300, 'protein': p, 'carbs': 20, 'fat': f+25, 'portion': '1 bowl', 'portion_th': '1 ชาม', 'tags': [], 'allergens': ['nuts']})

    # 3. Salads & Grilled (15 items)
    salads = [
        ('Papaya Salad', 'ส้มตำไทย', 120, 4, 25, 2, ['low_fat', 'vegetarian'], ['nuts']),
        ('Papaya Salad with Crab', 'ส้มตำปู', 110, 5, 22, 1, ['low_fat'], ['seafood']),
        ('Spicy Minced Pork', 'ลาบหมู', 180, 15, 8, 10, ['low_carb', 'keto'], []),
        ('Spicy Minced Chicken', 'ลาบไก่', 150, 16, 8, 5, ['low_carb', 'low_fat', 'high_protein'], []),
        ('Spicy Glass Noodle', 'ยำวุ้นเส้น', 200, 12, 35, 2, ['low_fat'], ['seafood']),
        ('Grilled Chicken', 'ไก่ย่าง', 160, 22, 0, 8, ['low_carb', 'high_protein'], []),
        ('Grilled Pork Neck', 'คอหมูย่าง', 280, 15, 5, 22, ['keto'], []),
        ('Steamed Fish Lemon', 'ปลานึ่งมะนาว', 140, 24, 2, 3, ['low_fat', 'low_carb', 'high_protein'], ['seafood']),
        ('Spicy Beef Salad', 'ยำเนื้อตก', 200, 20, 5, 10, ['low_carb', 'high_protein'], []),
        ('Spicy Seafood Salad', 'ยำรวมมิตรทะเล', 180, 18, 15, 3, ['low_fat'], ['seafood']),
        ('Nam Prik Kapi', 'น้ำพริกกะปิ', 80, 4, 10, 2, ['low_fat'], ['seafood']),
        ('Nam Prik Ong', 'น้ำพริกอ่อง', 150, 8, 12, 8, ['low_carb'], []),
        ('Mango Salad', 'ยำมะม่วง', 130, 2, 28, 1, ['low_fat', 'vegan'], ['nuts']),
        ('Corn Salad', 'ตำข้าวโพด', 160, 4, 30, 2, ['low_fat', 'vegetarian'], ['nuts']),
        ('Spicy Mushroom Salad', 'ยำเห็ดรวม', 100, 5, 15, 1, ['low_fat', 'vegan'], [])
    ]
    for en, th, c, p, crb, f, tg, alg in salads:
        db.append({'name': en, 'name_th': th, 'category': 'salad' if 'Salad' in en or 'Spicy' in en else 'protein', 'meal_types': ['lunch', 'dinner'], 'calories': c, 'protein': p, 'carbs': crb, 'fat': f, 'portion': '1 serving', 'portion_th': '1 จาน', 'tags': tg, 'allergens': alg})

    # 4. Breakfasts, Snacks, Drinks, Rice (20 items)
    misc = [
        ('Boiled Rice Pork', 'ข้าวต้มหมู', 220, 12, 35, 4, ['low_fat'], []),
        ('Boiled Rice Chicken', 'ข้าวต้มไก่', 200, 14, 35, 2, ['low_fat'], []),
        ('Thai Omelet', 'ไข่เจียว', 250, 12, 2, 22, ['keto'], ['eggs']),
        ('Boiled Egg', 'ไข่ต้ม', 70, 6, 0, 5, ['keto', 'high_protein'], ['eggs']),
        ('Steamed Egg', 'ไข่ตุ๋น', 120, 10, 2, 8, ['low_carb'], ['eggs', 'soy']),
        ('Hainanese Chicken Rice', 'ข้าวมันไก่', 500, 20, 55, 22, [], ['soy']),
        ('Fried Chicken Rice', 'ข้าวมันไก่ทอด', 600, 18, 60, 30, [], ['soy', 'gluten']),
        ('Steamed Rice', 'ข้าวสวย', 200, 4, 45, 0, ['vegan', 'low_fat'], []),
        ('Brown Rice', 'ข้าวกล้อง', 180, 5, 38, 1, ['vegan', 'low_fat', 'high_fiber'], []),
        ('Mango Sticky Rice', 'ข้าวเหนียวมะม่วง', 350, 3, 65, 10, ['vegan', 'dessert'], []),
        ('Thai Iced Tea', 'ชาไทย', 250, 2, 45, 8, ['drink'], ['dairy']),
        ('Coconut Water', 'น้ำมะพร้าว', 50, 0, 12, 0, ['drink', 'vegan'], []),
        ('Fresh Milk', 'นมสด', 150, 8, 12, 8, ['drink', 'high_protein'], ['dairy']),
        ('Soy Milk', 'น้ำเต้าหู้', 120, 7, 10, 4, ['drink', 'vegan'], ['soy']),
        ('Mixed Fruit', 'ผลไม้รวม', 100, 1, 25, 0, ['snack', 'vegan', 'high_fiber'], []),
        ('Yogurt', 'โยเกิร์ต', 120, 5, 15, 3, ['snack', 'vegetarian'], ['dairy']),
        ('Roasted Nuts', 'ถั่วอบ', 160, 6, 5, 14, ['snack', 'vegan', 'keto'], ['nuts']),
        ('Banana', 'กล้วยน้ำว้า', 90, 1, 23, 0, ['snack', 'vegan'], []),
        ('Papaya', 'มะละกอ', 60, 1, 15, 0, ['snack', 'vegan'], []),
        ('Guava', 'ฝรั่ง', 50, 1, 12, 0, ['snack', 'vegan', 'high_fiber'], [])
    ]
    for en, th, c, p, crb, f, tg, alg in misc:
        cat = 'drink' if 'drink' in tg else ('snack' if 'snack' in tg else ('dessert' if 'dessert' in tg else 'rice'))
        meals = ['snack'] if cat in ['drink', 'snack', 'dessert'] else ['breakfast', 'lunch', 'dinner']
        if th in ['ไข่ต้ม', 'ไข่ตุ๋น', 'ข้าวต้มหมู', 'ข้าวต้มไก่']: meals = ['breakfast', 'snack']
        db.append({'name': en, 'name_th': th, 'category': cat, 'meal_types': meals, 'calories': c, 'protein': p, 'carbs': crb, 'fat': f, 'portion': '1 serving', 'portion_th': '1 ที่', 'tags': tg, 'allergens': alg})

    return db

def _generate_exercise_db() -> List[Dict]:
    """Generates a database of 60+ exercises."""
    db = []
    exercises_data = [
        ('Push-ups', 'วิดพื้น', 'upper_body', 'Chest', 'none', 'intermediate', 15, 8, 'strength'),
        ('Knee Push-ups', 'วิดพื้นเข่าติดพื้น', 'upper_body', 'Chest', 'none', 'beginner', 10, 5, 'strength'),
        ('Pull-ups', 'ดึงข้อ', 'upper_body', 'Back', 'pull_up_bar', 'advanced', 20, 10, 'strength'),
        ('Dumbbell Rows', 'ดึงดัมเบล', 'upper_body', 'Back', 'dumbbell', 'intermediate', 15, 8, 'strength'),
        ('Dumbbell Bench Press', 'ดันดัมเบลอก', 'upper_body', 'Chest', 'dumbbell', 'intermediate', 18, 9, 'strength'),
        ('Shoulder Press', 'ดันไหล่', 'upper_body', 'Shoulders', 'dumbbell', 'intermediate', 15, 8, 'strength'),
        ('Lateral Raises', 'ยกดัมเบลด้านข้าง', 'upper_body', 'Shoulders', 'dumbbell', 'beginner', 10, 6, 'strength'),
        ('Bicep Curls', 'ยกดัมเบลหน้าแขน', 'upper_body', 'Biceps', 'dumbbell', 'beginner', 12, 6, 'strength'),
        ('Tricep Dips', 'ดันหลังแขน', 'upper_body', 'Triceps', 'none', 'intermediate', 12, 7, 'strength'),
        ('Plank', 'แพลงก์', 'core', 'Core', 'none', 'beginner', 10, 5, 'strength'),
        ('Crunches', 'ครันช์', 'core', 'Abs', 'none', 'beginner', 12, 6, 'strength'),
        ('Leg Raises', 'ยกขา', 'core', 'Abs', 'none', 'intermediate', 15, 7, 'strength'),
        ('Russian Twists', 'บิดตัวรัสเซีย', 'core', 'Obliques', 'none', 'intermediate', 15, 8, 'strength'),
        ('Mountain Climbers', 'ปีนเขา', 'core', 'Core', 'none', 'intermediate', 20, 10, 'cardio'),
        ('Squats', 'สควอท', 'lower_body', 'Legs', 'none', 'beginner', 18, 9, 'strength'),
        ('Lunges', 'ย่อเข่า', 'lower_body', 'Legs', 'none', 'beginner', 15, 8, 'strength'),
        ('Bulgarian Split Squats', 'สควอทขาเดียว', 'lower_body', 'Legs', 'dumbbell', 'advanced', 20, 10, 'strength'),
        ('Deadlifts', 'เดดลิฟต์', 'full_body', 'Back/Legs', 'barbell', 'advanced', 25, 12, 'strength'),
        ('Glute Bridges', 'ยกสะโพก', 'lower_body', 'Glutes', 'none', 'beginner', 12, 6, 'strength'),
        ('Calf Raises', 'เขย่งน่อง', 'lower_body', 'Calves', 'none', 'beginner', 10, 5, 'strength'),
        ('Burpees', 'เบอร์ปี', 'full_body', 'Full Body', 'none', 'advanced', 30, 15, 'cardio'),
        ('Jumping Jacks', 'กระโดดตบ', 'cardio', 'Full Body', 'none', 'beginner', 20, 10, 'cardio'),
        ('High Knees', 'วิ่งยกเข่าสูง', 'cardio', 'Full Body', 'none', 'intermediate', 25, 12, 'cardio'),
        ('Jump Rope', 'กระโดดเชือก', 'cardio', 'Full Body', 'none', 'intermediate', 30, 15, 'cardio'),
        ('Running (Jogging)', 'วิ่งจ๊อกกิ้ง', 'cardio', 'Legs', 'none', 'beginner', 0, 10, 'cardio'),
        ('Cycling', 'ปั่นจักรยาน', 'cardio', 'Legs', 'machine', 'beginner', 0, 8, 'cardio'),
        ('Rowing', 'กรรเชียง', 'cardio', 'Full Body', 'machine', 'intermediate', 0, 12, 'cardio'),
        ('Yoga Sun Salutation', 'โยคะไหว้พระอาทิตย์', 'flexibility', 'Full Body', 'none', 'beginner', 15, 5, 'flexibility'),
        ('Downward Dog', 'โยคะสุนัขก้มหน้า', 'flexibility', 'Full Body', 'none', 'beginner', 5, 3, 'flexibility'),
        ('Childs Pose', 'ท่าเด็ก', 'flexibility', 'Back', 'none', 'beginner', 2, 2, 'flexibility'),
        ('Stretching', 'ยืดเหยียดกล้ามเนื้อ', 'flexibility', 'Full Body', 'none', 'beginner', 5, 3, 'flexibility'),
        ('Kettlebell Swings', 'แกว่งเคตเทิลเบล', 'full_body', 'Full Body', 'dumbbell', 'intermediate', 25, 12, 'strength'),
        ('Box Jumps', 'กระโดดขึ้นกล่อง', 'lower_body', 'Legs', 'none', 'advanced', 25, 12, 'strength'),
        ('Wall Sit', 'นั่งพิงกำแพง', 'lower_body', 'Legs', 'none', 'beginner', 15, 8, 'strength'),
        ('Bicycle Crunches', 'ปั่นจักรยานอากาศ', 'core', 'Abs', 'none', 'intermediate', 15, 8, 'strength'),
        ('Flutter Kicks', 'เตะขาสลับ', 'core', 'Abs', 'none', 'intermediate', 15, 8, 'strength'),
        ('Side Plank', 'แพลงก์ด้านข้าง', 'core', 'Obliques', 'none', 'intermediate', 10, 6, 'strength'),
        ('Tricep Extensions', 'ยืดหลังแขน', 'upper_body', 'Triceps', 'dumbbell', 'beginner', 12, 6, 'strength'),
        ('Front Raises', 'ยกแขนไปข้างหน้า', 'upper_body', 'Shoulders', 'dumbbell', 'beginner', 10, 5, 'strength'),
        ('Reverse Fly', 'ยกแขนกางหลัง', 'upper_body', 'Back', 'dumbbell', 'intermediate', 15, 7, 'strength'),
        ('Barbell Squats', 'บาร์เบลสควอท', 'lower_body', 'Legs', 'barbell', 'advanced', 30, 12, 'strength'),
        ('Bench Press', 'ดันอกบาร์เบล', 'upper_body', 'Chest', 'barbell', 'advanced', 25, 10, 'strength'),
        ('Overhead Press', 'ดันไหล่บาร์เบล', 'upper_body', 'Shoulders', 'barbell', 'advanced', 25, 10, 'strength'),
        ('Lat Pulldown', 'ดึงหลัง', 'upper_body', 'Back', 'machine', 'intermediate', 15, 8, 'strength'),
        ('Leg Press', 'ดันขา', 'lower_body', 'Legs', 'machine', 'intermediate', 20, 10, 'strength'),
        ('Leg Curls', 'พับขา', 'lower_body', 'Hamstrings', 'machine', 'beginner', 15, 8, 'strength'),
        ('Leg Extensions', 'เตะขา', 'lower_body', 'Quads', 'machine', 'beginner', 15, 8, 'strength'),
        ('Cable Flyes', 'เคเบิลครอสโอเวอร์', 'upper_body', 'Chest', 'machine', 'intermediate', 15, 8, 'strength'),
        ('Seated Row', 'ดึงสายพาน', 'upper_body', 'Back', 'machine', 'intermediate', 15, 8, 'strength'),
        ('Resistance Band Squats', 'สควอทยางยืด', 'lower_body', 'Legs', 'resistance_band', 'beginner', 15, 7, 'strength'),
        ('Resistance Band Rows', 'ดึงยางยืด', 'upper_body', 'Back', 'resistance_band', 'beginner', 12, 6, 'strength'),
        ('Resistance Band Pull-aparts', 'กางยางยืด', 'upper_body', 'Shoulders', 'resistance_band', 'beginner', 10, 5, 'strength'),
        ('Treadmill Sprint', 'วิ่งสปรินต์', 'cardio', 'Legs', 'machine', 'advanced', 0, 15, 'cardio'),
        ('Elliptical', 'เครื่องเดินวงรี', 'cardio', 'Full Body', 'machine', 'beginner', 0, 9, 'cardio'),
        ('Stairmaster', 'เครื่องปีนบันได', 'cardio', 'Legs', 'machine', 'intermediate', 0, 12, 'cardio'),
        ('Shadow Boxing', 'ชกมวยลม', 'cardio', 'Full Body', 'none', 'intermediate', 20, 10, 'cardio'),
        ('Jumping Lunges', 'กระโดดย่อเข่า', 'lower_body', 'Legs', 'none', 'advanced', 25, 12, 'cardio'),
        ('Skaters', 'สเก็ตเตอร์', 'cardio', 'Legs', 'none', 'intermediate', 20, 10, 'cardio'),
        ('Bear Crawls', 'คลานหมี', 'full_body', 'Full Body', 'none', 'advanced', 25, 12, 'strength'),
        ('Superman', 'ซูเปอร์แมน', 'core', 'Lower Back', 'none', 'beginner', 10, 5, 'strength')
    ]
    for en, th, cat, musc, eq, diff, cps, cpm, typ in exercises_data:
        db.append({
            'name': en, 'name_th': th, 'category': cat, 'muscle_group': musc,
            'equipment': eq, 'difficulty': diff, 'calories_per_set': cps,
            'calories_per_minute': cpm, 'type': typ
        })
    return db

THAI_FOOD_DB = _generate_thai_food_db()
EXERCISE_DB = _generate_exercise_db()


# ==========================================
# 3. Main AI Functions
# ==========================================

def _get_seed(profile: dict, extra: str = "") -> int:
    seed_str = str(profile.get('name', '')) + str(profile.get('age', 0)) + extra
    return int(hashlib.md5(seed_str.encode()).hexdigest(), 16) % (10**8)

def analyze_health(profile: dict) -> dict:
    weight = profile.get('weight', 70)
    height = profile.get('height', 170)
    age = profile.get('age', 30)
    gender = profile.get('gender', 'male')
    target_weight = profile.get('target_weight', weight)
    goal = profile.get('goal', 'maintain')
    timeline = profile.get('timeline', 3)
    activity_level = profile.get('activity_level', 'sedentary')
    
    bmi = calculate_bmi(weight, height)
    bmr = calculate_bmr(weight, height, age, gender)
    tdee = calculate_tdee(bmr, activity_level)
    target_cal_data = calculate_target_calories(tdee, goal, weight, target_weight, timeline)
    macros = calculate_macros(target_cal_data['target_calories'], weight, goal)
    water = calculate_water_intake(weight, activity_level)
    
    # Generate Summaries
    health_summary = f"สวัสดีคุณ {profile.get('name', 'ผู้ใช้งาน')} จากข้อมูลของคุณ ตอนนี้คุณมีค่า BMI อยู่ที่ {bmi['value']:.1f} ({bmi['category']}) ระบบเผาผลาญพื้นฐาน (BMR) ของคุณคือ {int(bmr)} กิโลแคลอรีต่อวัน และเมื่อรวมกับกิจกรรมประจำวัน (TDEE) คุณใช้พลังงานประมาณ {int(tdee)} กิโลแคลอรีต่อวัน"
    
    goal_th = {'lose_weight': 'ลดน้ำหนัก', 'gain_weight': 'เพิ่มน้ำหนัก', 'build_muscle': 'สร้างกล้ามเนื้อ', 'maintain': 'รักษาน้ำหนัก'}.get(goal.lower(), 'ดูแลสุขภาพ')
    goal_analysis = f"เป้าหมายของคุณคือการ{goal_th}ให้ได้ {target_weight} กก. ภายใน {timeline} เดือน เป้าหมายนี้ต้องการการปรับพลังงานวันละ {int(abs(target_cal_data['deficit_or_surplus']))} กิโลแคลอรี เพื่อให้มีการเปลี่ยนแปลงน้ำหนักที่สัปดาห์ละ {abs(target_cal_data['weekly_change_kg']):.2f} กก. ซึ่งถือว่าเป็นเป้าหมายที่สามารถทำได้"
    
    recommendations = [
        f"ทานอาหารให้ได้ตามเป้าหมาย {int(target_cal_data['target_calories'])} กิโลแคลอรีต่อวัน",
        f"เน้นโปรตีนให้ได้วันละ {int(macros['protein_g'])} กรัม เพื่อเสริมสร้างกล้ามเนื้อ",
        f"ดื่มน้ำให้ได้อย่างน้อยวันละ {water} ลิตร",
        "ออกกำลังกายแบบคาร์ดิโอผสมผสานกับเวทเทรนนิ่งอย่างน้อย 3-4 วันต่อสัปดาห์",
        "นอนหลับพักผ่อนให้เพียงพอ 7-8 ชั่วโมงต่อวัน"
    ]
    
    warnings = []
    if age < 16 or age > 70:
        warnings.append("ข้อควรระวัง: อายุของคุณอยู่ในเกณฑ์ที่ควรปรึกษาแพทย์หรือผู้เชี่ยวชาญก่อนเริ่มโปรแกรมที่เข้มข้น")
    if bmi['value'] < 16 or bmi['value'] > 40:
        warnings.append("ข้อควรระวัง: ค่า BMI ของคุณอยู่ในเกณฑ์ที่มีความเสี่ยงสูง ควรปรึกษาแพทย์ก่อนควบคุมน้ำหนัก")
    if target_cal_data['target_calories'] < (1200 if gender.lower() == 'female' else 1500):
        warnings.append("ข้อควรระวัง: แคลอรี่เป้าหมายต่ำเกินไป อาจทำให้ขาดสารอาหารและเป็นอันตรายต่อสุขภาพ")
    if abs(target_cal_data['weekly_change_kg']) > 1.0:
        warnings.append("ข้อควรระวัง: เป้าหมายการเปลี่ยนแปลงน้ำหนักเร็วเกินไป (มากกว่า 1 กก./สัปดาห์) อาจทำให้สูญเสียมวลกล้ามเนื้อหรือส่งผลเสียต่อร่างกาย")
    warnings.append("คำเตือน: โปรแกรมนี้เป็นเพียงการประมาณการเบื้องต้น ควรปรึกษาแพทย์หรือนักกำหนดอาหารหากมีโรคประจำตัว")

    return {
        'bmi': bmi,
        'bmr': bmr,
        'tdee': tdee,
        'target_calories': target_cal_data['target_calories'],
        'deficit_or_surplus': target_cal_data['deficit_or_surplus'],
        'weekly_change_kg': target_cal_data['weekly_change_kg'],
        'macros': macros,
        'water_intake': water,
        'exercise_calories_target': abs(target_cal_data['deficit_or_surplus']) * 0.5 if goal == 'lose_weight' else 300,
        'health_summary': health_summary,
        'goal_analysis': goal_analysis,
        'recommendations': recommendations,
        'warnings': warnings
    }

def generate_meal_plan(profile: dict, analysis: dict) -> dict:
    random.seed(_get_seed(profile, str(datetime.now().date()) + "meals"))
    
    target_cal = analysis['target_calories']
    allergies = [a.lower() for a in profile.get('allergies', [])]
    prefs = [p.lower() for p in profile.get('food_preferences', [])]
    restrictions = [r.lower() for r in profile.get('dietary_restrictions', [])]
    
    valid_foods = []
    for food in THAI_FOOD_DB:
        conflict = any(alg in food['allergens'] for alg in allergies)
        if restrictions:
            if 'vegan' in restrictions and 'vegan' not in food['tags']: conflict = True
            elif 'vegetarian' in restrictions and 'vegetarian' not in food['tags'] and 'vegan' not in food['tags']: conflict = True
        if not conflict:
            valid_foods.append(food)
            
    if not valid_foods:
        valid_foods = THAI_FOOD_DB # Fallback if over-restricted
        
    def pick_meal(meal_type: str, target_c: float) -> dict:
        options = [f for f in valid_foods if meal_type in f['meal_types']]
        if not options: options = valid_foods
        
        # Boost preference weight
        weighted = []
        for opt in options:
            w = 1
            if any(p in opt['name'].lower() or p in opt['name_th'] for p in prefs): w = 5
            weighted.extend([opt] * w)
            
        chosen = random.choice(weighted)
        
        # Scale portion
        scale = target_c / chosen['calories'] if chosen['calories'] > 0 else 1.0
        # keep scale within reason
        scale = max(0.5, min(scale, 2.0))
        
        return {
            'meal_type': meal_type,
            'food_name': chosen['name'],
            'food_name_th': chosen['name_th'],
            'portion': f"{scale:.1f} x {chosen['portion']}",
            'portion_th': f"{scale:.1f} x {chosen['portion_th']}",
            'calories': round(chosen['calories'] * scale, 1),
            'protein': round(chosen['protein'] * scale, 1),
            'carbs': round(chosen['carbs'] * scale, 1),
            'fat': round(chosen['fat'] * scale, 1)
        }

    # Macro targets for meals
    # Breakfast 25%, Lunch 35%, Dinner 30%, Snack 10%
    meals = [
        pick_meal('breakfast', target_cal * 0.25),
        pick_meal('lunch', target_cal * 0.35),
        pick_meal('dinner', target_cal * 0.30),
        pick_meal('snack', target_cal * 0.10)
    ]
    
    total_c = sum(m['calories'] for m in meals)
    
    # Adjust total slightly if it missed
    if abs(total_c - target_cal) > target_cal * 0.05:
        correction = target_cal / total_c
        for m in meals:
            m['calories'] = round(m['calories'] * correction, 1)
            m['protein'] = round(m['protein'] * correction, 1)
            m['carbs'] = round(m['carbs'] * correction, 1)
            m['fat'] = round(m['fat'] * correction, 1)
        total_c = sum(m['calories'] for m in meals)
        
    return {
        'meals': meals,
        'total_calories': round(total_c, 1),
        'total_protein': round(sum(m['protein'] for m in meals), 1),
        'total_carbs': round(sum(m['carbs'] for m in meals), 1),
        'total_fat': round(sum(m['fat'] for m in meals), 1),
        'target_calories': target_cal
    }

def generate_workout_plan(profile: dict, analysis: dict) -> dict:
    random.seed(_get_seed(profile, str(datetime.now().date()) + "workout"))
    
    days_per_week = min(7, max(1, profile.get('exercise_days', 3)))
    level = profile.get('fitness_level', 'beginner').lower()
    equipment = [e.lower() for e in profile.get('equipment', ['none'])]
    goal = profile.get('goal', 'lose_weight').lower()
    
    valid_exercises = []
    for ex in EXERCISE_DB:
        if ex['difficulty'] == 'advanced' and level == 'beginner': continue
        if ex['difficulty'] == 'beginner' and level == 'advanced': continue
        if ex['equipment'] != 'none' and ex['equipment'] not in equipment: continue
        valid_exercises.append(ex)
        
    if not valid_exercises:
        valid_exercises = [e for e in EXERCISE_DB if e['equipment'] == 'none']
        
    days_th = ['จันทร์', 'อังคาร', 'พุธ', 'พฤหัสบดี', 'ศุกร์', 'เสาร์', 'อาทิตย์']
    days_en = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    workout_days = random.sample(range(7), days_per_week)
    
    workouts = []
    weekly_cal = 0.0
    
    for i in range(7):
        if i not in workout_days:
            workouts.append({
                'day': days_en[i],
                'day_th': days_th[i],
                'workout_type': 'Rest',
                'is_rest': True,
                'exercises': [],
                'total_calories': 0.0
            })
            continue
            
        # Determine focus based on goal
        if goal == 'lose_weight':
            focus = random.choice(['cardio', 'cardio', 'full_body', 'core'])
        elif goal in ['build_muscle', 'gain_weight']:
            focus = random.choice(['upper_body', 'lower_body', 'full_body'])
        else:
            focus = random.choice(['upper_body', 'lower_body', 'cardio', 'core'])
            
        pool = [e for e in valid_exercises if e['category'] == focus or e['type'] == focus]
        if len(pool) < 4: pool = valid_exercises
        
        chosen_ex = random.sample(pool, min(5, len(pool)))
        day_exercises = []
        day_cals = 0.0
        
        for ex in chosen_ex:
            if ex['calories_per_minute'] > 0:
                duration_mins = 15 if level == 'beginner' else (20 if level == 'intermediate' else 30)
                cal = ex['calories_per_minute'] * duration_mins
                day_exercises.append({
                    'name': ex['name'],
                    'name_th': ex['name_th'],
                    'sets': None,
                    'reps': None,
                    'duration': f"{duration_mins} mins",
                    'calories': round(cal, 1)
                })
                day_cals += cal
            else:
                sets = 3 if level == 'beginner' else (4 if level == 'intermediate' else 5)
                reps = "10-12" if goal != 'build_muscle' else "8-10"
                cal = ex['calories_per_set'] * sets
                day_exercises.append({
                    'name': ex['name'],
                    'name_th': ex['name_th'],
                    'sets': sets,
                    'reps': reps,
                    'duration': None,
                    'calories': round(cal, 1)
                })
                day_cals += cal
                
        workouts.append({
            'day': days_en[i],
            'day_th': days_th[i],
            'workout_type': focus.replace('_', ' ').title(),
            'is_rest': False,
            'exercises': day_exercises,
            'total_calories': round(day_cals, 1)
        })
        weekly_cal += day_cals
        
    return {
        'workouts': workouts,
        'weekly_calories': round(weekly_cal, 1)
    }

def generate_chat_response(message: str, profile: dict, analysis: dict) -> str:
    msg = message.lower()
    name = profile.get('name', 'คุณ')
    target_cal = int(analysis['target_calories'])
    goal_th = "ลดน้ำหนัก" if profile.get('goal') == 'lose_weight' else "ดูแลสุขภาพ"
    
    if "กินอะไรดี" in msg or "eat today" in msg:
        plan = generate_meal_plan(profile, analysis)
        lunch = next((m for m in plan['meals'] if m['meal_type'] == 'lunch'), plan['meals'][0])
        return f"สำหรับวันนี้ {name} แนะนำให้ลองทาน '{lunch['food_name_th']}' ({lunch['calories']} kcal) ครับ เหมาะกับเป้าหมาย{goal_th}ของคุณ และช่วยให้แคลอรี่ยังอยู่ในช่วงเป้าหมาย {target_cal} kcal ของวันนี้ครับ"
        
    elif "กินได้ไหม" in msg or "can i eat" in msg:
        return f"ถ้าอยากทาน สามารถทานได้ครับ {name} แค่พยายามกะปริมาณให้เหมาะสมไม่ให้แคลอรี่รวมวันนี้เกิน {target_cal} kcal ก็พอครับ อาหารทุกอย่างทานได้ แค่ต้องพอดีกับเป้าหมายของเราครับ"
        
    elif "เกิน" in msg or "exceeded" in msg:
        return f"ไม่เป็นไรเลยครับ {name}! การทานหลุดเป้าหมายบ้างเป็นเรื่องปกติ พรุ่งนี้เรากลับมาเริ่มใหม่ทานให้ได้ประมาณ {target_cal} kcal เหมือนเดิม ไม่ต้องลดปริมาณพรุ่งนี้เพื่อชดเชยนะครับ ค่อยๆ ทำตามแผนต่อไปอย่างสม่ำเสมอดีที่สุดครับ"
        
    elif "ไม่มีเวลา" in msg or "don't have time" in msg:
        return f"เข้าใจเลยครับ {name} ถ้าไม่มีเวลาไปยิม ลองจัดเวลาสัก 10-15 นาทีทำท่าบอดี้เวทง่ายๆ ที่บ้านอย่าง วิดพื้น หรือ สควอท ได้นะครับ หรือแค่เพิ่มการเดินระหว่างวันก็ช่วยเสริมการเผาผลาญสำหรับเป้าหมาย{goal_th}ของเราได้แล้วครับ"
        
    elif "แผน" in msg or "plan" in msg or "help me plan" in msg:
        return f"แน่นอนครับ {name}! แผนอาหารสำหรับ 1 วันที่เหมาะกับโควต้า {target_cal} kcal ของคุณ ผมแนะนำให้เน้นข้าวกล้อง หรือเนื้อสัตว์ไม่ติดมันเป็นหลัก เพื่อโปรตีนที่เพียงพอ ลองดูเมนูที่ระบบแนะนำในวันนี้ได้เลยครับ"
        
    else:
        return f"สวัสดีครับ {name} มีอะไรให้ผมช่วยแนะนำเกี่ยวกับสุขภาพ โภชนาการ หรือการออกกำลังกายไหมครับ? เป้าหมายโควต้าแคลอรี่ของคุณตอนนี้คือ {target_cal} kcal ต่อวัน ถ้ามีคำถามอะไรพิมพ์ถามมาได้เลยครับ!"

def analyze_progress(weight_history: list, target_weight: float, timeline_months: int, goal: str) -> dict:
    if not weight_history or len(weight_history) < 2:
        return {
            'trend': 'stable',
            'avg_weekly_change': 0.0,
            'projected_completion': 'ต้องการข้อมูลเพิ่มเติม',
            'on_track': True,
            'analysis': "ยังไม่มีข้อมูลน้ำหนักเพียงพอสำหรับการวิเคราะห์แนวโน้ม โปรดบันทึกน้ำหนักอย่างต่อเนื่อง",
            'recommendation': "แนะนำให้ชั่งน้ำหนักและบันทึกผลสัปดาห์ละ 1-2 ครั้งในช่วงเช้า"
        }
        
    start_weight = weight_history[0]['weight']
    current_weight = weight_history[-1]['weight']
    
    # Calculate weeks elapsed
    try:
        fmt = "%Y-%m-%d"
        d1 = datetime.strptime(weight_history[0]['date'], fmt)
        d2 = datetime.strptime(weight_history[-1]['date'], fmt)
        days = (d2 - d1).days
        weeks = max(1, days / 7)
    except:
        weeks = len(weight_history) - 1

    total_change = current_weight - start_weight
    avg_change = total_change / weeks
    
    goal_direction = -1 if goal == 'lose_weight' else (1 if goal in ['gain_weight', 'build_muscle'] else 0)
    
    if abs(avg_change) < 0.1:
        trend = 'stable'
    elif avg_change < 0:
        trend = 'decreasing'
    else:
        trend = 'increasing'
        
    on_track = False
    projected = "ไม่สามารถประเมินได้"
    analysis_text = ""
    rec_text = ""
    
    if goal_direction == -1: # Lose weight
        if trend == 'decreasing':
            on_track = True
            weeks_left = (current_weight - target_weight) / abs(avg_change) if avg_change != 0 else 0
            if weeks_left > 0:
                projected = f"อีกประมาณ {int(weeks_left)} สัปดาห์"
            else:
                projected = "ถึงเป้าหมายแล้ว!"
            analysis_text = f"ยอดเยี่ยมมาก! น้ำหนักของคุณลดลงเฉลี่ย {abs(avg_change):.2f} กก. ต่อสัปดาห์ ซึ่งอยู่ในเกณฑ์ที่ดีมาก"
            rec_text = "ทำต่อไปตามแผนปัจจุบัน ทั้งเรื่องอาหารและการออกกำลังกาย ร่างกายกำลังตอบสนองได้ดี"
        else:
            analysis_text = "ตอนนี้น้ำหนักของคุณค่อนข้างคงที่หรือเพิ่มขึ้นเล็กน้อย"
            rec_text = "ลองตรวจสอบปริมาณแคลอรี่ที่ทานอีกครั้ง หรือเพิ่มกิจกรรมทางกายระหว่างวันเพื่อเพิ่มการเผาผลาญ"
            
    elif goal_direction == 1: # Gain weight
        if trend == 'increasing':
            on_track = True
            weeks_left = (target_weight - current_weight) / avg_change if avg_change != 0 else 0
            if weeks_left > 0:
                projected = f"อีกประมาณ {int(weeks_left)} สัปดาห์"
            else:
                projected = "ถึงเป้าหมายแล้ว!"
            analysis_text = f"ทำได้ดีมาก! น้ำหนักของคุณเพิ่มขึ้นเฉลี่ย {avg_change:.2f} กก. ต่อสัปดาห์"
            rec_text = "รักษาระดับการทานอาหารให้ได้ตามเป้า เน้นโปรตีนควบคู่กับการเล่นเวทเพื่อสร้างกล้ามเนื้อ"
        else:
            analysis_text = "ตอนนี้น้ำหนักของคุณค่อนข้างคงที่หรือลดลง"
            rec_text = "คุณอาจจะต้องการพลังงานเพิ่มขึ้น ลองเพิ่มของว่างระหว่างมื้อ หรือเพิ่มปริมาณคาร์บและโปรตีนในมื้อหลัก"
            
    else: # Maintain
        if trend == 'stable':
            on_track = True
            analysis_text = "น้ำหนักของคุณคงที่ตามเป้าหมายที่ตั้งไว้"
            rec_text = "รักษารูปแบบการใช้ชีวิตในปัจจุบันไว้ ทั้งการกินและการออกกำลังกาย"
            projected = "รักษาระดับได้ดี"
        else:
            analysis_text = "น้ำหนักของคุณมีการเปลี่ยนแปลงจากเป้าหมายการรักษาน้ำหนัก"
            rec_text = "ปรับปริมาณอาหารให้เหมาะสมกับการใช้พลังงานในแต่ละวัน เพื่อให้น้ำหนักกลับมาคงที่"

    return {
        'trend': trend,
        'avg_weekly_change': round(avg_change, 2),
        'projected_completion': projected,
        'on_track': on_track,
        'analysis': analysis_text,
        'recommendation': rec_text
    }
