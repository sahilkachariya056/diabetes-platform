"""
app.py — Flask Backend for Diabetes Prediction Platform
PHASES 6, 7, 8, 12, 14
"""

import os
import json
import pickle
import numpy as np
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google import genai

"""
app.py — Flask Backend for Diabetes Prediction Platform
PHASES 6, 7, 8, 12, 14
"""

import os
import json
import pickle
import numpy as np

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google import genai


# ─────────────────────────────────────────────────────────────
# LOAD ENVIRONMENT VARIABLES
# ─────────────────────────────────────────────────────────────

load_dotenv()


# ─────────────────────────────────────────────────────────────
# CREATE FLASK APPLICATION
# ─────────────────────────────────────────────────────────────

app = Flask(__name__)


# ─────────────────────────────────────────────────────────────
# GEMINI AI CLIENT
# ─────────────────────────────────────────────────────────────

# Get Gemini API key from environment variable
api_key = os.getenv("GEMINI_API_KEY")

# Create Gemini client only if API key exists
if api_key:
    client = genai.Client(api_key=api_key)
else:
    client = None

# ─────────────────────────────────────────────────────────────
# LOAD MODEL BUNDLE
# ─────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, 'models', 'model.pkl'), 'rb') as f:
    BUNDLE = pickle.load(f)

MODEL    = BUNDLE['model']
SCALER   = BUNDLE['scaler']
FEATURES = BUNDLE['features']
SCALED   = BUNDLE['scaled']

with open(os.path.join(BASE_DIR, 'models', 'stats.json')) as f:
    STATS = json.load(f)

# ─────────────────────────────────────────────────────────────
# PHASE 7: AI RECOMMENDATION ENGINE
# ─────────────────────────────────────────────────────────────
def generate_recommendations(data):
    recs = []

    glucose = data.get('Glucose', 0)
    bmi     = data.get('BMI', 0)
    age     = data.get('Age', 0)
    insulin = data.get('Insulin', 0)
    bp      = data.get('BloodPressure', 0)
    preg    = data.get('Pregnancies', 0)
    dpf     = data.get('DiabetesPedigreeFunction', 0)

    # Glucose rules
    if glucose > 180:
        recs.append({
            'icon': '🩸', 'category': 'Critical',
            'color': '#E74C3C',
            'title': 'Dangerously High Glucose',
            'advice': 'Glucose is critically elevated. Seek immediate medical attention and avoid all sugary foods and drinks.'
        })
    elif glucose > 140:
        recs.append({
            'icon': '⚠️', 'category': 'Diet',
            'color': '#E67E22',
            'title': 'High Blood Glucose',
            'advice': 'Reduce sugar and refined carbohydrate intake. Eat more fiber-rich foods, whole grains, and vegetables. Monitor glucose daily.'
        })
    elif glucose > 100:
        recs.append({
            'icon': '🥗', 'category': 'Diet',
            'color': '#F39C12',
            'title': 'Pre-Diabetic Glucose Range',
            'advice': 'Glucose is slightly elevated. Limit processed sugars and opt for low-glycemic foods like lentils, oats, and leafy greens.'
        })

    # BMI rules
    if bmi > 40:
        recs.append({
            'icon': '🏋️', 'category': 'Weight',
            'color': '#E74C3C',
            'title': 'Severe Obesity',
            'advice': 'BMI indicates severe obesity. Consult a bariatric specialist. Start a medically supervised weight-loss program immediately.'
        })
    elif bmi > 30:
        recs.append({
            'icon': '🚴', 'category': 'Exercise',
            'color': '#E67E22',
            'title': 'Obesity - Exercise Required',
            'advice': 'Exercise at least 150 minutes per week. Include aerobic activity and strength training. A 5–10% weight reduction significantly lowers diabetes risk.'
        })
    elif bmi > 25:
        recs.append({
            'icon': '🏃', 'category': 'Fitness',
            'color': '#F39C12',
            'title': 'Overweight',
            'advice': 'Aim for 30 minutes of moderate exercise daily. Consider walking, swimming, or cycling. Small lifestyle changes make a big difference.'
        })

    # Age rules
    if age > 60:
        recs.append({
            'icon': '🏥', 'category': 'Checkup',
            'color': '#8E44AD',
            'title': 'Senior — Frequent Monitoring',
            'advice': 'At age 60+, get diabetes screening every 6 months. Monitor cholesterol and blood pressure. Stay physically active with low-impact exercises.'
        })
    elif age > 45:
        recs.append({
            'icon': '📋', 'category': 'Prevention',
            'color': '#2980B9',
            'title': 'Age Risk Factor',
            'advice': 'Adults over 45 are at higher risk. Schedule annual health checkups and fasting blood glucose tests. Maintain a healthy weight.'
        })

    # Insulin rules
    if insulin > 300:
        recs.append({
            'icon': '💉', 'category': 'Insulin',
            'color': '#E74C3C',
            'title': 'Very High Insulin Levels',
            'advice': 'Elevated insulin suggests insulin resistance. Consult an endocrinologist. Avoid refined carbs, increase physical activity, and consider medication review.'
        })
    elif insulin > 140:
        recs.append({
            'icon': '🔬', 'category': 'Metabolic',
            'color': '#E67E22',
            'title': 'Elevated Insulin',
            'advice': 'High insulin may indicate insulin resistance. Follow a low-carb diet, increase physical activity, and get a fasting insulin test.'
        })

    # Blood Pressure
    if bp > 90:
        recs.append({
            'icon': '❤️', 'category': 'Cardiovascular',
            'color': '#C0392B',
            'title': 'High Blood Pressure',
            'advice': 'High BP combined with diabetes risk is dangerous. Reduce sodium intake, avoid stress, and consider blood pressure medication after consulting a doctor.'
        })

    # Family history / DPF
    if dpf > 1.0:
        recs.append({
            'icon': '🧬', 'category': 'Genetics',
            'color': '#8E44AD',
            'title': 'High Genetic Risk',
            'advice': 'Your diabetes pedigree function suggests strong family history. Get tested regularly and adopt a preventive lifestyle early.'
        })

    # Positive reinforcement
    if glucose < 100 and bmi < 25:
        recs.append({
            'icon': '✅', 'category': 'Great Health',
            'color': '#27AE60',
            'title': 'Excellent Metabolic Markers',
            'advice': 'Glucose and BMI are in healthy ranges. Maintain this with regular exercise and a balanced diet. Keep up annual checkups.'
        })

    # General always-shown advice
    recs.append({
        'icon': '💧', 'category': 'Lifestyle',
        'color': '#2E86C1',
        'title': 'Daily Hydration & Sleep',
        'advice': 'Drink 8–10 glasses of water daily. Sleep 7–8 hours per night. Poor sleep increases cortisol, which elevates blood glucose.'
    })

    return recs


# ─────────────────────────────────────────────────────────────
# PHASE 6 & 8: RISK PREDICTION + EXPLAINABILITY
# ─────────────────────────────────────────────────────────────
def build_feature_vector(data):
    glucose = float(data.get('Glucose', 0))
    bmi     = float(data.get('BMI', 0))
    insulin = float(data.get('Insulin', 0))

    row = {
        'Pregnancies':              float(data.get('Pregnancies', 0)),
        'Glucose':                  glucose,
        'BloodPressure':            float(data.get('BloodPressure', 0)),
        'SkinThickness':            float(data.get('SkinThickness', 0)),
        'Insulin':                  insulin,
        'BMI':                      bmi,
        'DiabetesPedigreeFunction': float(data.get('DiabetesPedigreeFunction', 0)),
        'Age':                      float(data.get('Age', 0)),
        'GlucosePerBMI':            round(glucose / bmi, 3) if bmi else 0,
        'AgeRiskScore':             round(float(data.get('Age', 0)) * float(data.get('DiabetesPedigreeFunction', 0)), 3),
        'InsulinEfficiency':        round(glucose / (insulin + 1), 3),
    }
    return [row[f] for f in FEATURES]


# ─────────────────────────────────────────────────────────────
# PHASE 14: RULE-BASED CHATBOT (works without API key)
# ─────────────────────────────────────────────────────────────
CHAT_RULES = [
    (['what is diabetes', 'define diabetes', 'explain diabetes'],
     "Diabetes is a chronic condition where the body cannot properly regulate blood glucose (sugar) levels. There are two main types: Type 1 (autoimmune, the pancreas makes no insulin) and Type 2 (the body resists insulin or doesn't make enough). Gestational diabetes occurs during pregnancy."),

    (['symptom', 'sign of diabetes', 'how do i know'],
     "Common symptoms of diabetes include: frequent urination, excessive thirst, unexplained weight loss, blurry vision, slow-healing wounds, fatigue, and tingling in hands or feet. Type 2 can be silent for years — that's why screening matters!"),

    (['prevent', 'avoid diabetes', 'reduce risk'],
     "You can significantly reduce Type 2 diabetes risk by: maintaining a healthy weight (BMI < 25), exercising 150+ minutes/week, eating a low-glycemic diet (whole grains, vegetables, legumes), quitting smoking, limiting alcohol, and getting regular blood glucose screenings."),

    (['glucose', 'blood sugar', 'normal sugar level'],
     "Normal fasting blood glucose: 70–99 mg/dL. Pre-diabetes: 100–125 mg/dL. Diabetes: 126+ mg/dL. Post-meal (2 hours): under 140 mg/dL is normal. HbA1c under 5.7% is healthy, 5.7–6.4% is pre-diabetic, 6.5%+ is diabetic."),

    (['bmi', 'body mass index', 'healthy weight'],
     "BMI (Body Mass Index) = weight(kg) / height(m)². Ranges: Under 18.5 = Underweight | 18.5–24.9 = Normal | 25–29.9 = Overweight | 30+ = Obese. Higher BMI significantly raises Type 2 diabetes risk. Losing even 5–7% of body weight can reduce risk by 58%."),

    (['food', 'diet', 'eat', 'meal', 'nutrition'],
     "For diabetes prevention: Eat: vegetables, whole grains (oats, quinoa, brown rice), legumes (lentils, chickpeas), lean proteins (fish, chicken), healthy fats (avocado, nuts). Avoid: sugary drinks, white bread/rice, processed snacks, fried foods, and excessive red meat."),

    (['exercise', 'workout', 'physical activity', 'walk'],
     "Exercise improves insulin sensitivity and helps control blood glucose. Aim for 150 minutes of moderate aerobic activity per week (brisk walking, swimming, cycling). Add 2 days of strength training. Even a 10-minute walk after meals lowers post-meal blood sugar significantly."),

    (['insulin', 'insulin resistance'],
     "Insulin is a hormone that lets cells absorb glucose for energy. Insulin resistance means cells don't respond well to insulin, causing the pancreas to produce more. Over time, the pancreas can't keep up, leading to Type 2 diabetes. Exercise, weight loss, and diet directly improve insulin sensitivity."),

    (['medication', 'metformin', 'treatment'],
     "Common diabetes medications include: Metformin (first-line for Type 2, reduces liver glucose production), SGLT2 inhibitors (help kidneys excrete glucose), GLP-1 agonists (slow digestion, reduce appetite), and Insulin therapy. Always consult a doctor before starting or changing any medication."),

    (['how accurate', 'model accuracy', 'prediction accuracy', 'how does this work'],
     f"This platform uses a {STATS.get('model_name','Machine Learning')} model trained on diabetes health data. The model achieved {STATS['metrics']['accuracy']*100:.1f}% accuracy, {STATS['metrics']['f1']*100:.1f}% F1-score, and {STATS['metrics']['recall']*100:.1f}% recall. It analyzes 8 clinical inputs to estimate diabetes probability."),

    (['hello', 'hi', 'hey', 'good morning', 'good evening'],
     "Hello! 👋 I'm your HealthAI Assistant, specialized in diabetes and metabolic health. Ask me anything about diabetes symptoms, prevention, diet, exercise, or how this prediction platform works!"),

    (['thank', 'thanks', 'great', 'awesome'],
     "You're welcome! 😊 Remember: early prevention is the best medicine. Stay hydrated, exercise regularly, and get your blood glucose checked annually. I'm here anytime you have health questions!"),

    (['disclaimer', 'warning', 'medical advice'],
     "⚠️ Important: This platform is for educational and informational purposes ONLY. It is NOT a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider for medical decisions."),
]

def rule_based_chat(message):
    msg = message.lower().strip()
    for keywords, response in CHAT_RULES:
        if any(kw in msg for kw in keywords):
            return response
    return ("I'm not sure about that specific question. For diabetes-related topics, I can help with: "
            "symptoms, prevention, diet advice, glucose levels, BMI, exercise, medications, or how this "
            "prediction model works. What would you like to know?")


# ─────────────────────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────────────────────
@app.route('/')
def home():
    return render_template('index.html', stats=STATS)

@app.route('/prediction')
def prediction():
    return render_template('prediction.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', stats=STATS)

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')


@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        vec = build_feature_vector(data)
        arr = np.array(vec).reshape(1, -1)

        if SCALED:
            arr = SCALER.transform(arr)

        probability  = float(MODEL.predict_proba(arr)[0][1])
        risk_pct     = round(probability * 100, 1)
        health_score = round((1 - probability) * 100, 1)

        if risk_pct < 30:
            risk_level = 'Low'
            risk_color = '#27AE60'
            risk_icon  = '✅'
        elif risk_pct < 60:
            risk_level = 'Medium'
            risk_color = '#F39C12'
            risk_icon  = '⚠️'
        else:
            risk_level = 'High'
            risk_color = '#E74C3C'
            risk_icon  = '🚨'

        # Feature importance for top contributing factors
        importance = BUNDLE.get('feature_importance', {})
        top_factors = []
        base_keys   = ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness',
                        'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age']
        for feat in base_keys:
            if feat in importance:
                top_factors.append({'name': feat, 'importance': round(importance[feat] * 100, 1)})
        top_factors = sorted(top_factors, key=lambda x: x['importance'], reverse=True)[:5]

        recommendations = generate_recommendations(data)

        return jsonify({
            'risk_percentage':  risk_pct,
            'health_score':     health_score,
            'risk_level':       risk_level,
            'risk_color':       risk_color,
            'risk_icon':        risk_icon,
            'recommendations':  recommendations,
            'top_factors':      top_factors,
            'model_name':       BUNDLE.get('model_name', 'ML Model'),
            'confidence':       round(max(probability, 1 - probability) * 100, 1),
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ─────────────────────────────────────────────────────────────
# GEMINI AI CHATBOT
# ─────────────────────────────────────────────────────────────
@app.route('/chat', methods=['POST'])
def chat():
    try:
        # Get JSON data from the frontend
        data = request.get_json()

        # Get user's message
        message = data.get('message', '').strip()

        # Check if message is empty
        if not message:
            return jsonify({
                'error': 'Empty message'
            }), 400

        # ─────────────────────────────────────────────────────
        # TRY GEMINI AI
        # ─────────────────────────────────────────────────────

        # Get Gemini API key from environment variable
        api_key = os.getenv('GEMINI_API_KEY', '')

        # Check if Gemini API key and client are available
        if api_key and client:

            try:
                # Send user's question to Gemini
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=f"""
You are HealthAI, a friendly and professional healthcare assistant
specializing in diabetes prevention, management, and general
metabolic health.

Provide safe, evidence-based and easy-to-understand information.

Always remind users to consult a qualified healthcare professional
for medical decisions.

Do not diagnose diseases or prescribe medication.

Keep responses concise and empathetic.

User question:
{message}
"""
                )

                # Get Gemini's text response
                reply = response.text

                # Send Gemini response to frontend
                return jsonify({
                    'reply': reply,
                    'source': 'gemini'
                })

            except Exception as e:
                # Print Gemini error for debugging
                print("Gemini API Error:", e)

        # ─────────────────────────────────────────────────────
        # FALLBACK TO RULE-BASED CHATBOT
        # ─────────────────────────────────────────────────────

        # If Gemini is unavailable or fails,
        # use the predefined rule-based chatbot.
        reply = rule_based_chat(message)

        return jsonify({
            'reply': reply,
            'source': 'rules'
        })

    except Exception as e:
        # Handle unexpected errors
        return jsonify({
            'error': str(e)
        }), 500


if __name__ == '__main__':
    app.run(debug=False)
