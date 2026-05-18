# 🏥 HealthAI — Diabetes Prediction & Smart Healthcare Assistant Platform

A complete, production-ready AI-powered healthcare platform built with:
**Python · Flask · Scikit-learn · XGBoost · Chart.js · HTML/CSS/JS**

---

## 🎯 Features

| Feature | Details |
|---|---|
| 🤖 ML Model | Random Forest (GridSearchCV tuned, ~91% F1) |
| 📊 Risk Score | Probability 0–100% via `predict_proba()` |
| 💚 Health Score | `(1 - probability) × 100` |
| 🧠 Recommendations | Rule-based AI engine (glucose, BMI, age, insulin) |
| 📈 Dashboard | 7 interactive Chart.js visualizations |
| 💬 Chatbot | Rule-based + optional OpenAI GPT-3.5 |
| 🏗️ Backend | Flask REST API with 6 routes |
| 📱 Responsive | Mobile, tablet, desktop |

---

## 📁 Project Structure

```
diabetes_platform/
│
├── data/                   ← Dataset CSV (auto-generated)
├── models/                 ← model.pkl + stats.json (auto-generated)
├── notebooks/              ← Jupyter notebooks for EDA
├── templates/              ← Jinja2 HTML templates
│   ├── base.html           ← Fixed navbar + footer (shared layout)
│   ├── index.html          ← Home page with hero section
│   ├── prediction.html     ← Prediction form + results
│   ├── dashboard.html      ← Analytics dashboard (7 charts)
│   └── chatbot.html        ← AI chat interface
├── static/
│   ├── css/style.css       ← Complete healthcare UI styles
│   └── js/
│       ├── main.js         ← Navbar, hamburger, animations
│       ├── prediction.js   ← Form handling + API + results
│       ├── dashboard.js    ← All Chart.js chart code
│       └── chatbot.js      ← Chat messaging logic
│
├── app.py                  ← Flask backend (all routes)
├── train_model.py          ← ML pipeline (run once)
├── requirements.txt        ← Python dependencies
└── README.md
```

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Train the model (first time only)
```bash
python train_model.py
```
This generates `models/model.pkl` and `models/stats.json`.

### 3. Run the app
```bash
python app.py
```

### 4. Open in browser
```
http://localhost:5000
```

---

## 🔑 Optional: OpenAI Chatbot

Create a `.env` file:
```
OPENAI_API_KEY=sk-your-key-here
```
Without a key, the chatbot uses the built-in rule-based engine.

---

## 🌐 Pages

| Route | Page |
|---|---|
| `/` | Home — Hero + features + how-it-works |
| `/prediction` | Enter health data → get risk + recommendations |
| `/dashboard` | Analytics charts + model comparison |
| `/chatbot` | Ask health questions |
| `/predict` | POST API endpoint |
| `/chat` | POST chatbot endpoint |
| `/api/stats` | GET model stats JSON |

---

## 🧬 Input Features

| Feature | Description | Range |
|---|---|---|
| Pregnancies | Number of pregnancies | 0–17 |
| Glucose | Plasma glucose (mg/dL) | 44–199 |
| BloodPressure | Diastolic BP (mmHg) | 24–122 |
| SkinThickness | Triceps fold (mm) | 0–99 |
| Insulin | 2-hour serum insulin | 0–846 |
| BMI | Body Mass Index | 18–67 |
| DiabetesPedigreeFunction | Genetic risk score | 0.078–2.42 |
| Age | Age in years | 21–80 |

---

## ⚠️ Medical Disclaimer

> This platform is for **educational purposes only** and is **NOT** a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider.

---

## 🏗️ Tech Stack

- **Backend**: Python 3.10+, Flask 3.0, scikit-learn, XGBoost
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap Icons, Chart.js 4
- **ML**: Random Forest, Logistic Regression, XGBoost + GridSearchCV
- **AI**: Rule-based engine + optional OpenAI GPT-3.5
