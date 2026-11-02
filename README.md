

# Bank Fraud Detection (6.3M Transactions)

Fraud detection on a simulated mobile-money dataset. SQL (MySQL) for loading and analysis, Python (Random Forest) for modelling.

**Status:** Phase 1 SQL: in progress | Phase 2 Python: done | Phase 3 Power BI: not started

## Dataset
- Source: Kaggle "FraudScan-6M" (PaySim-style, **simulated** data). Add link here.
- 6,362,620 rows, 11 columns. 8,213 fraud rows (0.13%).

## Key findings
- Fraud occurs only in TRANSFER (0.77% of its rows) and CASH_OUT (0.18%). PAYMENT, CASH_IN and DEBIT have zero fraud.
- Balance mismatch alone is a weak signal: about 5.1M rows mismatch, only 8,213 are fraud.
- Random Forest (TRANSFER + CASH_OUT rows, 80/20 stratified split), fraud class: precision 0.9945, recall 0.9963, F1 0.9954, PR-AUC 0.998 (9 false alarms, 6 missed fraud).
- Accuracy is misleading here: predicting "not fraud" every time scores about 99.87%.

## Files
- `fraud_detection_day1.sql`: database, table, bulk load, verification and summary queries
- `01_eda.py`: data quality checks, EDA charts, 14 engineered features, Random Forest, evaluation
- `*.png`: 8 charts (class imbalance, fraud by type, fraud per day, feature importance, etc.)

## Limitations
- Data is simulated. Near-perfect scores reflect how the simulation generates fraud and would be lower on real data.
- Random train/test split, not time-based.

## How to run
Update the file paths inside both scripts. Run the SQL statement by statement (running LOAD DATA twice duplicates rows).
