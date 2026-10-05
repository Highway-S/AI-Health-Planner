import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

def calculate_bmr(weight, height, age, gender):
    # Mifflin-St Jeor Equation
    if gender == 0: # male
        return (10 * weight) + (6.25 * height) - (5 * age) + 5
    else: # female
        return (10 * weight) + (6.25 * height) - (5 * age) - 161

def calculate_tdee(bmr, activity_multiplier):
    return bmr * activity_multiplier

def calculate_target(tdee, goal):
    if goal == 0: # lose_weight
        return tdee - 500
    elif goal == 1: # maintain
        return tdee
    elif goal == 2: # gain_weight / build_muscle
        return tdee + 300
    return tdee

def create_and_train_model():
    print("Generating synthetic data...")
    n_samples = 1000
    np.random.seed(42)

    # Synthetic data generation
    # age: 18-70
    ages = np.random.randint(18, 70, n_samples)
    # gender: 0 (male), 1 (female)
    genders = np.random.randint(0, 2, n_samples)
    # height: 150-200 cm
    heights = np.random.uniform(150, 200, n_samples)
    # weight: 50-120 kg
    weights = np.random.uniform(50, 120, n_samples)
    
    # activity_level: 0 (sedentary) to 4 (very active)
    activity_levels = np.random.randint(0, 5, n_samples)
    activity_multipliers = np.array([1.2, 1.375, 1.55, 1.725, 1.9])
    
    # goal: 0 (lose), 1 (maintain), 2 (gain)
    goals = np.random.randint(0, 3, n_samples)

    X = np.column_stack((ages, genders, heights, weights, activity_levels, goals))
    y = np.zeros(n_samples)

    for i in range(n_samples):
        bmr = calculate_bmr(weights[i], heights[i], ages[i], genders[i])
        tdee = calculate_tdee(bmr, activity_multipliers[activity_levels[i]])
        target = calculate_target(tdee, goals[i])
        
        # Add random noise
        noise = np.random.normal(0, 100)
        y[i] = target + noise

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("Training RandomForestRegressor...")
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    print(f"Model Performance:")
    print(f"RMSE: {rmse:.2f} calories")
    print(f"R2 Score: {r2:.4f}")

    # Save model
    model_filename = 'model.pkl'
    joblib.dump(model, model_filename)
    print(f"Model saved to {model_filename}")

if __name__ == '__main__':
    create_and_train_model()
