import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")                      # charts files mein save hongi
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (classification_report, confusion_matrix,
                             average_precision_score, ConfusionMatrixDisplay)

DATA_PATH = 'D:/Data analytics Project/Bank Data set/Fraud.csv'
OUT_DIR = 'D:/Data analytics Project/bank_fraud_python/charts'
os.makedirs(OUT_DIR, exist_ok=True)

def save(name):
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, name), dpi=150)
    plt.close()

# ---------- 1. LOAD + DATA QUALITY ----------
df = pd.read_csv(DATA_PATH)
print("Shape:", df.shape)                  # expected (6362620, 11)
print("Nulls:\n", df.isnull().sum())
print("Duplicate rows:", df.duplicated().sum())
print("Fraud counts:\n", df['isFraud'].value_counts())

# ---------- 2. EDA CHARTS (8 mein se 6) ----------
counts = df['isFraud'].value_counts()
plt.figure(figsize=(6, 4))
plt.bar(['Normal', 'Fraud'], [counts[0], counts[1]])
plt.yscale('log'); plt.title('Class imbalance (log scale)')
save('01_class_imbalance.png')

plt.figure(figsize=(7, 4))
df['type'].value_counts().plot(kind='bar')
plt.title('Transactions by type'); plt.ylabel('Count')
save('02_txns_by_type.png')

plt.figure(figsize=(7, 4))
(df.groupby('type')['isFraud'].mean() * 100).sort_values().plot(kind='bar')
plt.title('Fraud rate by type (%)'); plt.ylabel('% fraud')
save('03_fraud_rate_by_type.png')

df['day'] = (df['step'] - 1) // 24 + 1
plt.figure(figsize=(9, 4))
df[df['isFraud'] == 1].groupby('day').size().plot()
plt.title('Fraud transactions per day'); plt.ylabel('Count')
save('04_fraud_per_day.png')

plt.figure(figsize=(7, 4))
plt.hist(np.log1p(df.loc[df['isFraud'] == 0, 'amount']), bins=60,
         alpha=0.5, density=True, label='Normal')
plt.hist(np.log1p(df.loc[df['isFraud'] == 1, 'amount']), bins=60,
         alpha=0.5, density=True, label='Fraud')
plt.legend(); plt.title('log(amount): fraud vs normal')
save('05_amount_distribution.png')

# ---------- 3. SIRF TRANSFER + CASH_OUT ----------
# SQL se pata chala: baaki 3 types mein fraud = 0.
data = df[df['type'].isin(['TRANSFER', 'CASH_OUT'])].copy()
del df                                     # RAM bachao
print("Modelling rows:", data.shape)

# ---------- 4. FEATURE ENGINEERING (14 features) ----------
data['type_is_transfer'] = (data['type'] == 'TRANSFER').astype(int)
data['log_amount'] = np.log1p(data['amount'])
data['errorBalanceOrig'] = data['newbalanceOrig'] + data['amount'] - data['oldbalanceOrg']
data['errorBalanceDest'] = data['oldbalanceDest'] + data['amount'] - data['newbalanceDest']
data['orig_emptied'] = ((data['newbalanceOrig'] == 0) & (data['oldbalanceOrg'] > 0)).astype(int)
data['amount_equals_balance'] = (data['amount'] == data['oldbalanceOrg']).astype(int)
data['amount_to_balance'] = data['amount'] / (data['oldbalanceOrg'] + 1)
data['dest_zero_both'] = ((data['oldbalanceDest'] == 0) & (data['newbalanceDest'] == 0)).astype(int)
data['hour'] = data['step'] % 24

features = ['type_is_transfer', 'amount', 'log_amount',
            'oldbalanceOrg', 'newbalanceOrig', 'oldbalanceDest', 'newbalanceDest',
            'errorBalanceOrig', 'errorBalanceDest', 'orig_emptied',
            'amount_equals_balance', 'amount_to_balance', 'dest_zero_both', 'hour']

plt.figure(figsize=(6, 4))                 # chart 6: kya "account khali" fraud ka ishara hai?
(data.groupby('orig_emptied')['isFraud'].mean() * 100).plot(kind='bar')
plt.title('Fraud rate: sender account emptied? (%)'); plt.ylabel('% fraud')
save('06_orig_emptied_fraud_rate.png')

# ---------- 5. TRAIN / TEST SPLIT ----------
X, y = data[features], data['isFraud']
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42)

# ---------- 6. RANDOM FOREST ----------
# Dheema ho to n_estimators=30 karo.
model = RandomForestClassifier(n_estimators=100, max_depth=12, min_samples_leaf=5,
                               class_weight='balanced_subsample',
                               n_jobs=-1, random_state=42)
model.fit(X_train, y_train)

# ---------- 7. EVALUATION ----------
y_pred = model.predict(X_test)
y_proba = model.predict_proba(X_test)[:, 1]
print(classification_report(y_test, y_pred, digits=4))
print("PR-AUC:", average_precision_score(y_test, y_proba))
cm = confusion_matrix(y_test, y_pred)
print("Confusion matrix:\n", cm)

fig, ax = plt.subplots(figsize=(5, 4))
ConfusionMatrixDisplay(cm, display_labels=['Normal', 'Fraud']).plot(ax=ax, values_format='d')
save('07_confusion_matrix.png')

plt.figure(figsize=(7, 5))
pd.Series(model.feature_importances_, index=features).sort_values().plot(kind='barh')
plt.title('Feature importance')
save('08_feature_importance.png')

print("Done. Charts folder:", OUT_DIR)