// ==========================================================================
// AI Health & Fitness Planner - Bilingual Frontend Engine (TH / EN)
// ==========================================================================

// Application State
let currentLang = localStorage.getItem('health_planner_lang') || 'th';
let currentUserId = null;
let currentProfile = null;
let currentAnalysis = null;
let currentMealPlan = null;
let currentWorkoutPlan = null;
let weightHistory = [];
let weightChart = null;

// Translation Dictionary
const i18n = {
    th: {
        app_title: "🏋️ AI Health Planner",
        form_main_title: "การประเมินสุขภาพเฉพาะบุคคล",
        form_main_sub: "กรุณากรอกข้อมูลเพื่อให้ AI วางแผนสุขภาพและโภชนาการที่เหมาะสมกับคุณ",
        sec_personal: "ข้อมูลส่วนตัว (Personal Information)",
        label_name: "ชื่อ - นามสกุล",
        label_age: "อายุ (ปี)",
        label_gender: "เพศ",
        opt_select_gender: "เลือกเพศ...",
        opt_male: "ชาย (Male)",
        opt_female: "หญิง (Female)",
        label_height: "ส่วนสูง (ซม.)",
        label_weight: "น้ำหนักปัจจุบัน (กก.)",
        sec_goal: "เป้าหมายสุขภาพ (Health Goals)",
        label_goal: "เป้าหมายหลัก",
        opt_select_goal: "เลือกเป้าหมาย...",
        opt_lose: "ลดน้ำหนัก (Lose Weight)",
        opt_gain: "เพิ่มน้ำหนัก (Gain Weight)",
        opt_maintain: "รักษาน้ำหนัก (Maintain Weight)",
        opt_muscle: "เพิ่มกล้ามเนื้อ (Build Muscle)",
        label_target_weight: "น้ำหนักเป้าหมาย (กก.)",
        label_timeline: "ระยะเวลาที่ต้องการบรรลุเป้าหมาย",
        opt_select_time: "เลือกระยะเวลา...",
        opt_1m: "1 เดือน (1 Month)",
        opt_3m: "3 เดือน (3 Months)",
        opt_6m: "6 เดือน (6 Months)",
        opt_12m: "12 เดือน (12 Months)",
        sec_lifestyle: "ไลฟ์สไตล์และการออกกำลังกาย (Lifestyle & Fitness)",
        label_activity: "ระดับกิจกรรมประจำวัน",
        opt_select_act: "เลือกระดับกิจกรรม...",
        act_sedentary: "นั่งทำงานเป็นหลัก / ไม่ออกกำลังกาย (Sedentary)",
        act_light: "ออกกำลังกายเบาๆ 1-3 วัน/สัปดาห์ (Light)",
        act_moderate: "ออกกำลังกายปานกลาง 3-5 วัน/สัปดาห์ (Moderate)",
        act_active: "ออกกำลังกายหนัก 6-7 วัน/สัปดาห์ (Active)",
        act_very_active: "ออกกำลังกายหนักมาก / นักกีฬา (Very Active)",
        label_days: "จำนวนวันที่สามารถออกกำลังกายได้",
        label_fitness: "ระดับความพร้อมในการออกกำลังกาย",
        opt_select_fit: "เลือกระดับความฟิต...",
        fit_beg: "เริ่มต้น (Beginner)",
        fit_int: "ปานกลาง (Intermediate)",
        fit_adv: "สูง (Advanced)",
        label_equip: "อุปกรณ์ออกกำลังกายที่มี",
        eq_none: "ไม่มีอุปกรณ์ (Bodyweight)",
        eq_dumbbell: "ดัมเบล (Dumbbell)",
        eq_barbell: "บาร์เบล (Barbell)",
        eq_machine: "เครื่องออกกำลังกาย (Machine)",
        eq_band: "ยางยืด (Resistance Band)",
        eq_bar: "บาร์โหน (Pull-up Bar)",
        sec_diet: "พฤติกรรมการรับประทานอาหาร (Dietary Preferences)",
        label_food_pref: "ประเภทอาหารที่ชอบ",
        label_diet_rest: "ข้อจำกัดด้านอาหาร",
        label_allergies: "อาหารที่แพ้",
        btn_generate: "🤖 สร้างแผนสุขภาพเฉพาะบุคคลด้วย AI",
        dash_hello: "สวัสดีคุณ",
        dash_sub: "นี่คือแผนสุขภาพและโภชนาการเฉพาะบุคคลของคุณที่สร้างด้วย AI",
        tab_overview: "ภาพรวม (Overview)",
        tab_nutrition: "แผนอาหาร (Nutrition)",
        tab_workout: "ตารางออกกำลังกาย (Workout)",
        tab_progress: "ติดตามผล (Progress)",
        card_cur_weight: "น้ำหนักปัจจุบัน",
        card_tar_weight: "น้ำหนักเป้าหมาย",
        card_target_cal: "Calories วันนี้",
        card_burn_cal: "Calories ที่เผาผลาญ",
        card_water: "น้ำที่ควรดื่ม",
        card_ai_summary: "AI Health Summary (บทวิเคราะห์สุขภาพ)",
        card_goal_analysis: "Goal Analysis (การวิเคราะห์เป้าหมาย)",
        card_recs: "คำแนะนำเฉพาะบุคคล (Recommendations)",
        dash_disclaimer: "คำเตือน: ข้อมูลจากระบบนี้จัดทำขึ้นเพื่อให้คำแนะนำด้านสุขภาพเบื้องต้น ไม่สามารถใช้แทนคำวินิจฉัยหรือคำแนะนำจากแพทย์ นักโภชนาการ หรือผู้เชี่ยวชาญด้านสุขภาพได้",
        nutri_daily_target: "Daily Calorie Target:",
        nutri_consumed: "รับประทานรวม",
        macro_protein: "Protein (โปรตีน)",
        macro_carbs: "Carbs (คาร์โบไฮเดรต)",
        macro_fat: "Fat (ไขมัน)",
        nutri_meal_plan: "Meal Plan (ตารางอาหารประจำวัน)",
        btn_regen_meals: "สร้างเมนูใหม่",
        th_meal: "มื้อ",
        th_food: "อาหาร",
        th_portion: "ปริมาณ",
        th_total: "รวมทั้งหมด",
        work_summary_title: "สรุปการออกกำลังกายประจำสัปดาห์",
        work_active_days: "จำนวนวันออกกำลังกาย:",
        work_burned_cals: "แคลอรีที่เผาผลาญรวม",
        work_plan_title: "Workout Plan (โปรแกรมออกกำลังกาย 7 วัน)",
        btn_regen_work: "สร้างโปรแกรมใหม่",
        th_day: "วัน",
        th_type: "ประเภท",
        th_exercise: "ท่าฝึก (Exercise)",
        th_sets: "เซ็ต (Sets)",
        th_reps: "ครั้ง (Reps)",
        th_duration: "เวลา (Duration)",
        prog_log_title: "บันทึกน้ำหนัก (Log Weight)",
        btn_save_weight: "บันทึก",
        prog_analysis_title: "AI Progress Analysis (วิเคราะห์แนวโน้ม)",
        prog_chart_title: "Weight Trend (กราฟแนวโน้มน้ำหนัก)",
        prog_history_title: "Weight History (ประวัติการบันทึก)",
        th_date: "วันที่ (Date)",
        th_rec_weight: "น้ำหนัก (กก.)",
        th_rec_change: "เปลี่ยนแปลง",
        toast_success_gen: "สร้างแผนสุขภาพเฉพาะบุคคลด้วย AI เรียบร้อยแล้ว!",
        toast_regen_meals: "สร้างเมนูอาหารใหม่สำเร็จ!",
        toast_regen_workouts: "สร้างโปรแกรมออกกำลังกายใหม่สำเร็จ!",
        toast_weight_logged: "บันทึกน้ำหนักเรียบร้อยแล้ว",
        rest_day_desc: "พักฟื้นกล้ามเนื้อ ดื่มน้ำ และนอนหลับให้เพียงพอ",
        rest_label: "พักผ่อน (Rest)",
        days_unit: "วัน / สัปดาห์",
        chart_actual: "น้ำหนักจริง (กก.)",
        chart_target: "น้ำหนักเป้าหมาย (Target)",
        bmi_under: "น้ำหนักน้อย",
        bmi_normal: "น้ำหนักปกติ",
        bmi_over: "น้ำหนักเกิน",
        bmi_obese: "อ้วน"
    },
    en: {
        app_title: "🏋️ AI Health Planner",
        form_main_title: "Personal Health Assessment",
        form_main_sub: "Please enter your details to generate your tailored AI nutrition & workout plan",
        sec_personal: "Personal Information",
        label_name: "Full Name",
        label_age: "Age (Years)",
        label_gender: "Gender",
        opt_select_gender: "Select gender...",
        opt_male: "Male",
        opt_female: "Female",
        label_height: "Height (cm)",
        label_weight: "Current Weight (kg)",
        sec_goal: "Health Goals",
        label_goal: "Primary Goal",
        opt_select_goal: "Select goal...",
        opt_lose: "Lose Weight",
        opt_gain: "Gain Weight",
        opt_maintain: "Maintain Weight",
        opt_muscle: "Build Muscle",
        label_target_weight: "Target Weight (kg)",
        label_timeline: "Target Timeline",
        opt_select_time: "Select timeline...",
        opt_1m: "1 Month",
        opt_3m: "3 Months",
        opt_6m: "6 Months",
        opt_12m: "12 Months",
        sec_lifestyle: "Lifestyle & Fitness",
        label_activity: "Daily Activity Level",
        opt_select_act: "Select activity level...",
        act_sedentary: "Sedentary (Desk job / Little to no exercise)",
        act_light: "Light (Light exercise 1-3 days/week)",
        act_moderate: "Moderate (Moderate exercise 3-5 days/week)",
        act_active: "Active (Hard exercise 6-7 days/week)",
        act_very_active: "Very Active (Intense training / Athlete)",
        label_days: "Exercise Days per Week",
        label_fitness: "Fitness Experience Level",
        opt_select_fit: "Select fitness level...",
        fit_beg: "Beginner",
        fit_int: "Intermediate",
        fit_adv: "Advanced",
        label_equip: "Available Equipment",
        eq_none: "No Equipment (Bodyweight)",
        eq_dumbbell: "Dumbbells",
        eq_barbell: "Barbell",
        eq_machine: "Gym Machines",
        eq_band: "Resistance Bands",
        eq_bar: "Pull-up Bar",
        sec_diet: "Dietary Preferences",
        label_food_pref: "Food Preferences",
        label_diet_rest: "Dietary Restrictions",
        label_allergies: "Allergies",
        btn_generate: "🤖 Generate My Plan with AI",
        dash_hello: "Hello",
        dash_sub: "Here is your personalized AI-driven health and nutrition plan",
        tab_overview: "Overview",
        tab_nutrition: "Nutrition",
        tab_workout: "Workout",
        tab_progress: "Progress",
        card_cur_weight: "Current Weight",
        card_tar_weight: "Target Weight",
        card_target_cal: "Target Calories",
        card_burn_cal: "Calories to Burn",
        card_water: "Recommended Water",
        card_ai_summary: "AI Health Summary",
        card_goal_analysis: "Goal Analysis",
        card_recs: "Personal Recommendations",
        dash_disclaimer: "Disclaimer: This system provides general health guidance and does not replace medical consultation from physicians, nutritionists, or fitness professionals.",
        nutri_daily_target: "Daily Calorie Target:",
        nutri_consumed: "consumed",
        macro_protein: "Protein",
        macro_carbs: "Carbohydrates",
        macro_fat: "Fats",
        nutri_meal_plan: "Daily Meal Plan",
        btn_regen_meals: "Regenerate Meals",
        th_meal: "Meal",
        th_food: "Food Item",
        th_portion: "Portion",
        th_total: "Total",
        work_summary_title: "Weekly Workout Summary",
        work_active_days: "Active Exercise Days:",
        work_burned_cals: "Total Calories Burned",
        work_plan_title: "7-Day Workout Program",
        btn_regen_work: "Regenerate Workouts",
        th_day: "Day",
        th_type: "Type",
        th_exercise: "Exercise",
        th_sets: "Sets",
        th_reps: "Reps",
        th_duration: "Duration",
        prog_log_title: "Log Weight",
        btn_save_weight: "Save",
        prog_analysis_title: "AI Progress Analysis",
        prog_chart_title: "Weight Trend Chart",
        prog_history_title: "Weight History Log",
        th_date: "Date",
        th_rec_weight: "Weight (kg)",
        th_rec_change: "Change",
        toast_success_gen: "Personalized AI Health Plan created successfully!",
        toast_regen_meals: "New meal plan generated!",
        toast_regen_workouts: "New workout program generated!",
        toast_weight_logged: "Weight entry recorded successfully",
        rest_day_desc: "Rest, hydrate, and allow your muscles to recover.",
        rest_label: "Rest Day",
        days_unit: "days / week",
        chart_actual: "Actual Weight (kg)",
        chart_target: "Target Weight (kg)",
        bmi_under: "Underweight",
        bmi_normal: "Normal Weight",
        bmi_over: "Overweight",
        bmi_obese: "Obese"
    }
};

// Meal and Day Translations
const mealNames = {
    th: { breakfast: "มื้อเช้า", lunch: "มื้อกลางวัน", dinner: "มื้อเย็น", snack: "ของว่าง" },
    en: { breakfast: "Breakfast", lunch: "Lunch", dinner: "Dinner", snack: "Snack" }
};

const dayNames = {
    th: { Monday: "จันทร์", Tuesday: "อังคาร", Wednesday: "พุธ", Thursday: "พฤหัสบดี", Friday: "ศุกร์", Saturday: "เสาร์", Sunday: "อาทิตย์" },
    en: { Monday: "Monday", Tuesday: "Tuesday", Wednesday: "Wednesday", Thursday: "Thursday", Friday: "Friday", Saturday: "Saturday", Sunday: "Sunday" }
};

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
    const initialSection = window.INITIAL_SECTION || 'assessment';
    const initialUserId = window.INITIAL_USER_ID;
    
    setupEventListeners();
    applyLanguage(currentLang);

    if (initialUserId && initialSection === 'dashboard') {
        currentUserId = parseInt(initialUserId);
        loadDashboard(currentUserId);
    } else {
        showSection('assessment-section');
    }
});

// Setup Event Listeners
function setupEventListeners() {
    // Form submission
    const assessmentForm = document.getElementById('assessment-form');
    if (assessmentForm) {
        assessmentForm.addEventListener('submit', submitAssessment);
    }

    // Tab Navigation
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const targetId = e.currentTarget.getAttribute('data-target');
            switchTab(targetId);
        });
    });

    // Language switcher buttons
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const lang = e.target.getAttribute('data-lang');
            setLanguage(lang);
        });
    });

    // Regenerate Buttons
    const regenerateMealsBtn = document.getElementById('regenerate-meals-btn');
    if (regenerateMealsBtn) {
        regenerateMealsBtn.addEventListener('click', regenerateMeals);
    }

    const regenerateWorkoutsBtn = document.getElementById('regenerate-workouts-btn');
    if (regenerateWorkoutsBtn) {
        regenerateWorkoutsBtn.addEventListener('click', regenerateWorkouts);
    }

    // Weight Log Form
    const weightLogForm = document.getElementById('weight-log-form');
    if (weightLogForm) {
        weightLogForm.addEventListener('submit', addWeightEntry);
        const dateInput = document.getElementById('weight-date');
        if (dateInput) {
            dateInput.value = todayLocal();
            dateInput.max = todayLocal();
        }
    }
}

// Language Switching
function setLanguage(lang) {
    currentLang = lang;
    localStorage.setItem('health_planner_lang', lang);
    applyLanguage(lang);
    
    if (currentProfile && currentAnalysis) {
        renderAll();
    }
}

function applyLanguage(lang) {
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.classList.toggle('active', btn.getAttribute('data-lang') === lang);
    });

    const dict = i18n[lang] || i18n.th;
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (dict[key]) {
            el.innerHTML = dict[key];
        }
    });

    // Placeholders
    if (lang === 'en') {
        const nameInput = document.getElementById('name');
        if (nameInput) nameInput.placeholder = "e.g. John Doe";
        const foodPref = document.getElementById('food_preferences');
        if (foodPref) foodPref.placeholder = "e.g. Thai food, Clean food, Chicken, Eggs";
        const dietRest = document.getElementById('dietary_restrictions');
        if (dietRest) dietRest.placeholder = "e.g. Vegetarian, Halal, Keto";
        const allergies = document.getElementById('allergies');
        if (allergies) allergies.placeholder = "e.g. Nuts, Dairy, Seafood, Eggs";
    } else {
        const nameInput = document.getElementById('name');
        if (nameInput) nameInput.placeholder = "เช่น สมชาย ใจดี";
        const foodPref = document.getElementById('food_preferences');
        if (foodPref) foodPref.placeholder = "เช่น อาหารไทย, อาหารคลีน, ชอบกินไข่/อกไก่";
        const dietRest = document.getElementById('dietary_restrictions');
        if (dietRest) dietRest.placeholder = "เช่น มังสวิรัติ, ฮาลาล, คีโต";
        const allergies = document.getElementById('allergies');
        if (allergies) allergies.placeholder = "เช่น ถั่ว, นม, อาหารทะเล, กุ้ง";
    }
}

// UI State Management
function showSection(sectionId) {
    document.querySelectorAll('.section-container').forEach(sec => sec.classList.add('hidden'));
    const sec = document.getElementById(sectionId);
    if (sec) {
        sec.classList.remove('hidden');
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function switchTab(tabId) {
    document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    
    const targetPane = document.getElementById(tabId);
    if (targetPane) targetPane.classList.add('active');
    
    const targetBtn = document.querySelector(`.tab-btn[data-target="${tabId}"]`);
    if (targetBtn) targetBtn.classList.add('active');

    if (tabId === 'progress-tab' && weightChart) {
        setTimeout(() => weightChart.resize(), 100);
    }
}

function setBtnLoading(btn, isLoading) {
    if (!btn) return;
    const span = btn.querySelector('span');
    const spinner = btn.querySelector('.spinner');
    if (isLoading) {
        btn.disabled = true;
        if (span) span.classList.add('hidden');
        if (spinner) spinner.classList.remove('hidden');
    } else {
        btn.disabled = false;
        if (span) span.classList.remove('hidden');
        if (spinner) spinner.classList.add('hidden');
    }
}

function showNotification(message, type = 'success') {
    const toast = document.getElementById('toast');
    const toastMsg = document.getElementById('toast-message');
    if (!toast || !toastMsg) return;

    toastMsg.textContent = message;
    toast.className = 'toast show';
    if (type === 'error') {
        toast.classList.add('toast-error');
    } else {
        toast.classList.add('toast-success');
    }
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3500);
}

// Escape untrusted text before inserting it into innerHTML
function escapeHtml(value) {
    return String(value ?? '').replace(/[&<>"']/g, c => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }[c]));
}

// Local-timezone YYYY-MM-DD (toISOString() is UTC and can be off by one day in Thailand)
function todayLocal() {
    const d = new Date();
    const pad = n => String(n).padStart(2, '0');
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}

// Fetch API Helper
async function apiCall(url, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    };
    if (data && (method === 'POST' || method === 'PUT')) {
        options.body = JSON.stringify(data);
    }
    const res = await fetch(url, options);
    if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP error! status: ${res.status}`);
    }
    return res.json();
}

// Form Submission & Analysis
async function submitAssessment(e) {
    e.preventDefault();
    
    const form = e.target;
    const btn = document.getElementById('generate-btn');
    setBtnLoading(btn, true);

    try {
        const formData = new FormData(form);
        const data = {};
        
        for (let [key, val] of formData.entries()) {
            if (key !== 'equipment') {
                data[key] = val;
            }
        }
        
        const selectedEquipment = Array.from(form.querySelectorAll('input[name="equipment"]:checked')).map(el => el.value);
        data.equipment = selectedEquipment.length > 0 ? selectedEquipment.join(', ') : 'none';
        
        // 1. Create Profile
        const profileRes = await apiCall('/api/profile', 'POST', data);
        if (!profileRes.success || !profileRes.user_id) {
            throw new Error('Could not save profile');
        }
        currentUserId = profileRes.user_id;
        currentProfile = profileRes.profile || data;

        // 2. Fetch AI Analysis, Meal Plan, Workout Plan
        const [analysisRes, mealRes, workoutRes] = await Promise.all([
            apiCall('/api/analyze', 'POST', { user_id: currentUserId }),
            apiCall('/api/meal-plan', 'POST', { user_id: currentUserId }),
            apiCall('/api/workout-plan', 'POST', { user_id: currentUserId })
        ]);

        currentAnalysis = analysisRes;
        currentMealPlan = mealRes;
        currentWorkoutPlan = workoutRes;
        
        // Initial weight entry
        weightHistory = [
            { date: todayLocal(), weight: parseFloat(data.weight) }
        ];

        // 3. Render Dashboard
        renderAll();
        
        const navName = document.getElementById('nav-user-name');
        if (navName) navName.textContent = data.name;
        const userNav = document.getElementById('user-greeting-nav');
        if (userNav) userNav.classList.remove('hidden');

        showSection('dashboard-section');
        switchTab('overview-tab');
        
        window.history.pushState(null, '', `/dashboard/${currentUserId}`);
        
        const dict = i18n[currentLang] || i18n.th;
        showNotification(dict.toast_success_gen);
    } catch (err) {
        console.error('Error submitting assessment:', err);
        showNotification(err.message || 'Error creating plan', 'error');
    } finally {
        setBtnLoading(btn, false);
    }
}

// Load Dashboard from Backend
async function loadDashboard(userId) {
    try {
        const data = await apiCall(`/api/dashboard/${userId}`, 'GET');
        currentProfile = data.profile;
        currentAnalysis = data.analysis;
        currentMealPlan = data.meal_plan;
        currentWorkoutPlan = data.workout_plan;
        weightHistory = data.weight_history || [];

        renderAll();

        const navName = document.getElementById('nav-user-name');
        if (navName && currentProfile) navName.textContent = currentProfile.name;
        const userNav = document.getElementById('user-greeting-nav');
        if (userNav) userNav.classList.remove('hidden');

        showSection('dashboard-section');
    } catch (err) {
        console.error('Error loading dashboard:', err);
        showNotification('User profile not found', 'error');
        showSection('assessment-section');
    }
}

function renderAll() {
    renderOverview();
    renderNutrition();
    renderWorkout();
    renderProgress();
}

function renderOverview() {
    if (!currentProfile || !currentAnalysis) return;
    
    const prof = currentProfile;
    const anl = currentAnalysis;
    const dict = i18n[currentLang] || i18n.th;
    
    const dashName = document.getElementById('dashboard-name');
    if (dashName) dashName.textContent = prof.name;
    
    // BMI Card
    const bmiVal = anl.bmi ? anl.bmi.value.toFixed(1) : '--';
    let bmiCatText = anl.bmi ? anl.bmi.category : '--';
    const bmiColor = anl.bmi ? anl.bmi.color : 'green';
    
    if (currentLang === 'en' && anl.bmi) {
        if (anl.bmi.value < 18.5) bmiCatText = dict.bmi_under;
        else if (anl.bmi.value < 25) bmiCatText = dict.bmi_normal;
        else if (anl.bmi.value < 30) bmiCatText = dict.bmi_over;
        else bmiCatText = dict.bmi_obese;
    }
    
    document.getElementById('metric-bmi').textContent = bmiVal;
    const badge = document.getElementById('metric-bmi-badge');
    badge.textContent = bmiCatText;
    badge.className = `badge badge-${bmiColor === 'blue' ? 'normal' : (bmiColor === 'orange' ? 'warning' : (bmiColor === 'red' ? 'danger' : 'success'))}`;
    
    // Metric Values
    document.getElementById('metric-weight').textContent = prof.weight;
    document.getElementById('metric-target-weight').textContent = prof.target_weight;
    document.getElementById('metric-tdee').textContent = Math.round(anl.tdee);
    document.getElementById('metric-calories').textContent = Math.round(anl.target_calories);
    
    const exerciseCal = anl.exercise_calories_target || (currentWorkoutPlan ? currentWorkoutPlan.weekly_calories / (currentProfile.exercise_days || 3) : 250);
    document.getElementById('metric-burn').textContent = Math.round(exerciseCal);
    
    const proteinG = anl.macros ? Math.round(anl.macros.protein_g) : Math.round(prof.weight * 1.8);
    document.getElementById('metric-protein').textContent = proteinG;
    document.getElementById('metric-water').textContent = anl.water_intake || (prof.weight * 0.033).toFixed(1);
    
    // AI Summary Texts
    document.getElementById('ai-health-summary').textContent = anl.health_summary || (currentLang === 'th' ? 'สุขภาพโดยรวมของคุณอยู่ในเกณฑ์ดี' : 'Your overall health metrics are in good standing.');
    document.getElementById('goal-analysis').innerHTML = `<p>${escapeHtml(anl.goal_analysis || (currentLang === 'th' ? 'แผนการบรรลุเป้าหมายได้รับการจัดเตรียมแล้ว' : 'Your target goal plan is configured.'))}</p>`;
    
    // Recommendations
    const recList = document.getElementById('recommendations-list');
    recList.innerHTML = '';
    const recs = anl.recommendations || [];
    recs.forEach(r => {
        const li = document.createElement('li');
        li.textContent = r;
        recList.appendChild(li);
    });

    // Warnings
    const warnContainer = document.getElementById('warnings-container');
    warnContainer.innerHTML = '';
    const warns = anl.warnings || [];
    warns.forEach(w => {
        const div = document.createElement('div');
        div.className = 'alert alert-warning';
        div.innerHTML = `<i class="fas fa-exclamation-triangle" aria-hidden="true"></i> <div>${escapeHtml(w)}</div>`;
        warnContainer.appendChild(div);
    });
}

function renderNutrition() {
    if (!currentMealPlan || !currentAnalysis) return;
    
    const mp = currentMealPlan;
    const anl = currentAnalysis;
    const dict = i18n[currentLang] || i18n.th;
    
    const targetCal = Math.round(anl.target_calories);
    const consumedCal = Math.round(mp.total_calories);
    
    document.getElementById('nutrition-cal-target').textContent = targetCal;
    document.getElementById('nutrition-cal-consumed').textContent = `${consumedCal} kcal`;
    
    // Guard against divide-by-zero / NaN when targets are missing
    const pctOf = (val, target) => target > 0 ? Math.round((val / target) * 100) : 0;
    const pct = Math.min(100, pctOf(consumedCal, targetCal));
    document.getElementById('calorie-progress').style.width = pct + '%';
    
    const targetProtein = Math.round(anl.macros ? anl.macros.protein_g : 100);
    const targetCarbs = Math.round(anl.macros ? anl.macros.carbs_g : 200);
    const targetFat = Math.round(anl.macros ? anl.macros.fat_g : 50);

    const consumedProtein = Math.round(mp.total_protein);
    const consumedCarbs = Math.round(mp.total_carbs);
    const consumedFat = Math.round(mp.total_fat);

    document.getElementById('macro-protein').textContent = `${consumedProtein} / ${targetProtein}`;
    document.getElementById('macro-protein-pct').textContent = pctOf(consumedProtein, targetProtein) + '%';
    
    document.getElementById('macro-carbs').textContent = `${consumedCarbs} / ${targetCarbs}`;
    document.getElementById('macro-carbs-pct').textContent = pctOf(consumedCarbs, targetCarbs) + '%';
    
    document.getElementById('macro-fat').textContent = `${consumedFat} / ${targetFat}`;
    document.getElementById('macro-fat-pct').textContent = pctOf(consumedFat, targetFat) + '%';
    
    // Meal Table
    const tbody = document.querySelector('#meal-plan-table tbody');
    tbody.innerHTML = '';
    
    const mNames = mealNames[currentLang] || mealNames.th;
    const meals = mp.meals || [];
    meals.forEach(m => {
        const tr = document.createElement('tr');
        const mealType = mNames[m.meal_type] || m.meal_type;
        const foodName = currentLang === 'en' ? (m.food_name || m.name || m.food_name_th) : (m.food_name_th || m.food_name || m.name);
        const portion = currentLang === 'en' ? (m.portion || m.portion_th || '1 serving') : (m.portion_th || m.portion || '1 ที่');

        tr.innerHTML = `
            <td><strong>${escapeHtml(mealType)}</strong></td>
            <td>${escapeHtml(foodName)}</td>
            <td>${escapeHtml(portion)}</td>
            <td><strong>${Math.round(m.calories)}</strong> kcal</td>
            <td>${Math.round(m.protein)}g</td>
            <td>${Math.round(m.carbs)}g</td>
            <td>${Math.round(m.fat)}g</td>
        `;
        tbody.appendChild(tr);
    });
    
    document.getElementById('total-cals').innerHTML = `<strong>${consumedCal} kcal</strong>`;
    document.getElementById('total-protein').innerHTML = `<strong>${consumedProtein}g</strong>`;
    document.getElementById('total-carbs').innerHTML = `<strong>${consumedCarbs}g</strong>`;
    document.getElementById('total-fat').innerHTML = `<strong>${consumedFat}g</strong>`;
}

async function regenerateMeals() {
    const btn = document.getElementById('regenerate-meals-btn');
    const icon = btn ? btn.querySelector('i') : null;
    if (icon) icon.classList.add('fa-spin');
    
    try {
        const res = await apiCall('/api/regenerate-meals', 'POST', { user_id: currentUserId });
        currentMealPlan = res;
        renderNutrition();
        const dict = i18n[currentLang] || i18n.th;
        showNotification(dict.toast_regen_meals);
    } catch(e) {
        showNotification('Error generating new meals', 'error');
    } finally {
        if (icon) icon.classList.remove('fa-spin');
    }
}

function renderWorkout() {
    if (!currentWorkoutPlan) return;
    const wp = currentWorkoutPlan;
    const dict = i18n[currentLang] || i18n.th;
    const dNames = dayNames[currentLang] || dayNames.th;
    
    const totalWorkouts = wp.workouts || [];
    const activeDays = totalWorkouts.filter(w => !w.is_rest).length;
    const totalWeeklyCal = Math.round(wp.weekly_calories || 0);

    document.getElementById('workout-total-days').textContent = `${activeDays} ${dict.days_unit}`;
    document.getElementById('workout-total-cals').textContent = `${totalWeeklyCal} kcal`;
    
    const tbody = document.querySelector('#workout-plan-table tbody');
    tbody.innerHTML = '';
    
    totalWorkouts.forEach(w => {
        const isRest = w.is_rest;
        const dayLabel = dNames[w.day] || w.day_th || w.day;
        const workoutType = isRest ? dict.rest_label : (w.workout_type || 'Workout');
        
        if (isRest || !w.exercises || w.exercises.length === 0) {
            const tr = document.createElement('tr');
            tr.style.backgroundColor = '#f8fafc';
            tr.innerHTML = `
                <td><strong>${escapeHtml(dayLabel)}</strong></td>
                <td><span class="badge badge-normal">${dict.rest_label}</span></td>
                <td colspan="4" class="text-medium">${dict.rest_day_desc}</td>
                <td>0 kcal</td>
            `;
            tbody.appendChild(tr);
        } else {
            w.exercises.forEach((ex, exIdx) => {
                const tr = document.createElement('tr');
                const exName = currentLang === 'en' ? (ex.name || ex.name_th) : (ex.name_th || ex.name);
                const sets = ex.sets ? `${ex.sets}` : '-';
                const reps = ex.reps ? `${ex.reps}` : '-';
                const duration = ex.duration ? `${ex.duration}` : '-';
                const cals = Math.round(ex.calories || 0);

                tr.innerHTML = `
                    <td>${exIdx === 0 ? `<strong>${escapeHtml(dayLabel)}</strong>` : ''}</td>
                    <td>${exIdx === 0 ? `<span class="badge badge-warning">${escapeHtml(workoutType)}</span>` : ''}</td>
                    <td><strong>${escapeHtml(exName)}</strong></td>
                    <td>${sets}</td>
                    <td>${reps}</td>
                    <td>${duration}</td>
                    <td>${cals > 0 ? cals + ' kcal' : '-'}</td>
                `;
                tbody.appendChild(tr);
            });
        }
    });
}

async function regenerateWorkouts() {
    const btn = document.getElementById('regenerate-workouts-btn');
    const icon = btn ? btn.querySelector('i') : null;
    if (icon) icon.classList.add('fa-spin');
    
    try {
        const res = await apiCall('/api/regenerate-workouts', 'POST', { user_id: currentUserId });
        currentWorkoutPlan = res;
        renderWorkout();
        const dict = i18n[currentLang] || i18n.th;
        showNotification(dict.toast_regen_workouts);
    } catch(e) {
        showNotification('Error generating workouts', 'error');
    } finally {
        if (icon) icon.classList.remove('fa-spin');
    }
}

function renderProgress() {
    const analysisCard = document.getElementById('progress-analysis-text');
    // ISO dates (YYYY-MM-DD) sort correctly as strings and avoid timezone shifts
    const sortedDesc = [...weightHistory].sort((a,b) => String(b.date).localeCompare(String(a.date)));
    
    const tbody = document.querySelector('#weight-history-table tbody');
    tbody.innerHTML = '';
    
    sortedDesc.forEach((entry, idx) => {
        let change = '-';
        if (idx < sortedDesc.length - 1) {
            const prev = sortedDesc[idx+1].weight;
            const diffNum = Number(entry.weight) - Number(prev);
            const diff = diffNum.toFixed(1);
            if (diffNum >= 0.05) change = `<span class="text-danger">+${diff} kg</span>`;
            else if (diffNum <= -0.05) change = `<span class="text-success">${diff} kg</span>`;
            else change = `0.0 kg`;
        }
        
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${escapeHtml(entry.date)}</td>
            <td><strong>${Number(entry.weight).toFixed(1)}</strong> kg</td>
            <td>${change}</td>
        `;
        tbody.appendChild(tr);
    });

    if (weightHistory.length >= 2 && currentProfile) {
        const first = sortedDesc[sortedDesc.length - 1].weight;
        const latest = sortedDesc[0].weight;
        const diff = (latest - first).toFixed(1);
        if (analysisCard) {
            if (currentLang === 'th') {
                analysisCard.textContent = `น้ำหนักของคุณเปลี่ยนแปลง ${diff} kg จากจุดเริ่มต้น AI ขอแนะนำให้รักษาแผนโภชนาการและออกกำลังกายอย่างต่อเนื่อง`;
            } else {
                analysisCard.textContent = `Your weight has shifted ${diff} kg from starting point. Keep following your tailored nutrition and exercise schedule!`;
            }
        }
    }

    createWeightChart();
}

async function addWeightEntry(e) {
    e.preventDefault();
    const dateInput = document.getElementById('weight-date').value;
    const weightInput = parseFloat(document.getElementById('weight-value').value);
    
    if (!dateInput || isNaN(weightInput)) {
        showNotification(currentLang === 'th' ? 'กรุณาระบุน้ำหนักให้ถูกต้อง' : 'Please provide a valid weight value', 'error');
        return;
    }

    try {
        const res = await apiCall('/api/progress', 'POST', {
            user_id: currentUserId,
            weight: weightInput,
            date: dateInput
        });
        
        if (res.history) {
            weightHistory = res.history;
        } else {
            weightHistory.push({ date: dateInput, weight: weightInput });
        }
        
        weightHistory.sort((a,b) => String(a.date).localeCompare(String(b.date)));
        if (res.profile) currentProfile = res.profile;

        // Render first, then show the server analysis so it is not overwritten
        renderProgress();
        renderOverview();
        if (res.analysis && res.analysis.analysis) {
            const analysisCard = document.getElementById('progress-analysis-text');
            if (analysisCard) analysisCard.textContent = res.analysis.analysis;
        }
        const dict = i18n[currentLang] || i18n.th;
        showNotification(dict.toast_weight_logged);
        document.getElementById('weight-value').value = '';
    } catch(err) {
        showNotification('Error logging weight', 'error');
    }
}

function createWeightChart() {
    const ctx = document.getElementById('weightChart');
    if (!ctx) return;
    
    const dict = i18n[currentLang] || i18n.th;
    const dataAsc = [...weightHistory].sort((a,b) => String(a.date).localeCompare(String(b.date)));
    const labels = dataAsc.map(d => d.date);
    const dataPoints = dataAsc.map(d => d.weight);
    const target = currentProfile ? parseFloat(currentProfile.target_weight) : 65;
    const targetData = labels.map(() => target);
    
    if (weightChart) {
        weightChart.destroy();
    }
    
    const allVals = [...dataPoints, target];
    const minVal = Math.floor(Math.min(...allVals) - 2);
    const maxVal = Math.ceil(Math.max(...allVals) + 2);

    weightChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: dict.chart_actual,
                    data: dataPoints,
                    borderColor: '#10B981',
                    backgroundColor: 'rgba(16, 185, 129, 0.15)',
                    borderWidth: 3,
                    pointBackgroundColor: '#10B981',
                    pointRadius: 6,
                    fill: true,
                    tension: 0.3
                },
                {
                    label: dict.chart_target,
                    data: targetData,
                    borderColor: '#94A3B8',
                    borderWidth: 2,
                    borderDash: [6, 6],
                    pointRadius: 0,
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom' },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.raw} kg`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    min: minVal,
                    max: maxVal,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}
