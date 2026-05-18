"""
PHASES 2-8: Data Pipeline, ML Training, and Model Saving
=========================================================
Run this script ONCE to train and save model.pkl
"""

import pandas as pd
import numpy as np
import pickle
import json
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, confusion_matrix)
from xgboost import XGBClassifier

print("=" * 60)
print("  DIABETES PREDICTION PLATFORM - MODEL TRAINER")
print("=" * 60)

# ─────────────────────────────────────────────────────────────
# PHASE 2: GENERATE REALISTIC PIMA INDIANS DIABETES DATASET
# ─────────────────────────────────────────────────────────────
print("\nPHASE 2: Generating Dataset...")

np.random.seed(42)
N = 768

def make_dataset(n):
    age            = np.random.randint(21, 81, n)
    bmi            = np.clip(np.random.normal(32, 7, n), 18.0, 67.1).round(1)
    glucose        = np.clip(np.random.normal(121, 32, n), 44, 199).astype(int)
    blood_pressure = np.clip(np.random.normal(72, 12, n), 24, 122).astype(int)
    insulin        = np.clip(np.random.exponential(80, n), 0, 846).astype(int)
    skin_thickness = np.clip(np.random.normal(29, 11, n), 0, 99).astype(int)
    dpf            = np.clip(np.random.exponential(0.47, n), 0.078, 2.42).round(3)
    pregnancies    = np.clip(np.random.poisson(3.8, n), 0, 17).astype(int)

    log_odds = (
        -8.0
        + 0.036 * glucose
        + 0.075 * bmi
        + 0.032 * age
        + 0.012 * insulin
        + 0.85  * dpf
        + 0.085 * pregnancies
    )
    prob = 1 / (1 + np.exp(-log_odds))
    outcome = (np.random.uniform(0, 1, n) < prob).astype(int)

    return pd.DataFrame({
        'Pregnancies':              pregnancies,
        'Glucose':                  glucose,
        'BloodPressure':            blood_pressure,
        'SkinThickness':            skin_thickness,
        'Insulin':                  insulin,
        'BMI':                      bmi,
        'DiabetesPedigreeFunction': dpf,
        'Age':                      age,
        'Outcome':                  outcome,
    })

df = make_dataset(N)
df.to_csv('data/diabetes.csv', index=False)
print(f"  Dataset shape: {df.shape[0]} rows x {df.shape[1]} cols")
print(f"  Diabetic: {df['Outcome'].sum()} | Non-Diabetic: {(df['Outcome']==0).sum()}")

# ─────────────────────────────────────────────────────────────
# PHASE 3: DATA CLEANING & PREPROCESSING
# ─────────────────────────────────────────────────────────────
print("\nPHASE 3: Cleaning & Preprocessing...")

zero_cols = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']
for col in zero_cols:
    median_val = df[col].replace(0, np.nan).median()
    df[col] = df[col].replace(0, median_val)

before = len(df)
df = df.drop_duplicates().reset_index(drop=True)
print(f"  Duplicates removed: {before - len(df)}")

def cap_outliers(series, factor=3.0):
    Q1, Q3 = series.quantile(0.25), series.quantile(0.75)
    IQR = Q3 - Q1
    return series.clip(Q1 - factor * IQR, Q3 + factor * IQR)

for col in df.columns[:-1]:
    df[col] = cap_outliers(df[col])

df['GlucosePerBMI']     = (df['Glucose'] / df['BMI']).round(3)
df['AgeRiskScore']      = (df['Age'] * df['DiabetesPedigreeFunction']).round(3)
df['InsulinEfficiency'] = (df['Glucose'] / (df['Insulin'] + 1)).round(3)
print("  Missing values imputed, outliers capped, features engineered")

# ─────────────────────────────────────────────────────────────
# PHASE 5: TRAIN MULTIPLE MODELS
# ─────────────────────────────────────────────────────────────
print("\nPHASE 5: Training Models...")

FEATURES = ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness',
            'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age',
            'GlucosePerBMI', 'AgeRiskScore', 'InsulinEfficiency']

X = df[FEATURES]
y = df['Outcome']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s  = scaler.transform(X_test)

results = {}

# 1. Logistic Regression
lr = LogisticRegression(max_iter=1000, random_state=42)
lr.fit(X_train_s, y_train)
lr_pred = lr.predict(X_test_s)
results['Logistic Regression'] = {
    'model': lr, 'scaled': True,
    'acc':  accuracy_score(y_test, lr_pred),
    'prec': precision_score(y_test, lr_pred),
    'rec':  recall_score(y_test, lr_pred),
    'f1':   f1_score(y_test, lr_pred),
}

# 2. Random Forest with GridSearch
rf_params = {'n_estimators': [100, 200], 'max_depth': [5, 10, None]}
rf_gs = GridSearchCV(RandomForestClassifier(random_state=42), rf_params,
                     cv=5, scoring='f1', n_jobs=-1)
rf_gs.fit(X_train, y_train)
rf_best = rf_gs.best_estimator_
rf_pred = rf_best.predict(X_test)
results['Random Forest'] = {
    'model': rf_best, 'scaled': False,
    'acc':  accuracy_score(y_test, rf_pred),
    'prec': precision_score(y_test, rf_pred),
    'rec':  recall_score(y_test, rf_pred),
    'f1':   f1_score(y_test, rf_pred),
}

# 3. XGBoost with GridSearch
xgb_params = {'n_estimators': [100, 200], 'max_depth': [3, 5],
               'learning_rate': [0.05, 0.1]}
xgb_gs = GridSearchCV(
    XGBClassifier(random_state=42, eval_metric='logloss'),
    xgb_params, cv=5, scoring='f1', n_jobs=-1
)
xgb_gs.fit(X_train, y_train)
xgb_best = xgb_gs.best_estimator_
xgb_pred = xgb_best.predict(X_test)
results['XGBoost'] = {
    'model': xgb_best, 'scaled': False,
    'acc':  accuracy_score(y_test, xgb_pred),
    'prec': precision_score(y_test, xgb_pred),
    'rec':  recall_score(y_test, xgb_pred),
    'f1':   f1_score(y_test, xgb_pred),
}

print(f"\n  {'Model':<25} {'Accuracy':>9} {'Precision':>10} {'Recall':>8} {'F1':>7}")
print("  " + "-" * 60)
for name, r in results.items():
    print(f"  {name:<25} {r['acc']:>9.4f} {r['prec']:>10.4f} {r['rec']:>8.4f} {r['f1']:>7.4f}")

best_name = max(results, key=lambda k: results[k]['f1'])
best_info  = results[best_name]
best_model = best_info['model']
print(f"\n  Best Model: {best_name} (F1={best_info['f1']:.4f})")

cv_data   = X_train_s if best_info['scaled'] else X_train
cv_scores = cross_val_score(best_model, cv_data, y_train, cv=10, scoring='f1')
print(f"  10-Fold CV F1: {cv_scores.mean():.4f} +/- {cv_scores.std():.4f}")

if best_name in ('Random Forest', 'XGBoost'):
    feat_imp = dict(zip(FEATURES, best_model.feature_importances_.round(4)))
else:
    feat_imp = dict(zip(FEATURES, np.abs(best_model.coef_[0]).round(4)))

feat_imp_sorted = dict(sorted(feat_imp.items(), key=lambda x: x[1], reverse=True))

# ─────────────────────────────────────────────────────────────
# SAVE ARTIFACTS
# ─────────────────────────────────────────────────────────────
print("\nSaving model artifacts...")

bundle = {
    'model':              best_model,
    'scaler':             scaler,
    'features':           FEATURES,
    'scaled':             best_info['scaled'],
    'model_name':         best_name,
    'metrics': {
        'accuracy':  round(best_info['acc'], 4),
        'precision': round(best_info['prec'], 4),
        'recall':    round(best_info['rec'], 4),
        'f1':        round(best_info['f1'], 4),
        'cv_mean':   round(float(cv_scores.mean()), 4),
        'cv_std':    round(float(cv_scores.std()), 4),
    },
    'feature_importance': feat_imp_sorted,
    'all_results': {
        k: {m: round(v, 4) for m, v in v.items() if m not in ('model', 'scaled')}
        for k, v in results.items()
    },
}

with open('models/model.pkl', 'wb') as f:
    pickle.dump(bundle, f)

stats = {
    'model_name':         best_name,
    'metrics':            bundle['metrics'],
    'feature_importance': feat_imp_sorted,
    'all_results':        bundle['all_results'],
    'dataset_stats': {
        'total_records': int(len(df)),
        'diabetic':      int(df['Outcome'].sum()),
        'non_diabetic':  int((df['Outcome'] == 0).sum()),
        'avg_glucose':   round(float(df['Glucose'].mean()), 1),
        'avg_bmi':       round(float(df['BMI'].mean()), 1),
        'avg_age':       round(float(df['Age'].mean()), 1),
    }
}

with open('models/stats.json', 'w') as f:
    json.dump(stats, f, indent=2)

print("  models/model.pkl saved")
print("  models/stats.json saved")
print("\n" + "=" * 60)
print("  TRAINING COMPLETE - Ready to launch app.py")
print("=" * 60)
