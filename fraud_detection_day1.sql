/* ============================================================
   Bank Fraud Detection System - Phase 1 (SQL), Day 1
   Author   : Aqib
   Database : MySQL 8.0
   Dataset  : Kaggle "FraudScan-6M" (PaySim-style simulated mobile
              money transactions), file: Fraud.csv (~493 MB)
   Rows     : 6,362,620 | Fraud rows: 8,213 (about 0.13%)
   NOTE     : Run statement by statement (Ctrl + Enter), NOT the
              whole file at once. Running LOAD DATA twice
              duplicates every row.
   ============================================================ */


/* ---------- 1. DATABASE ---------- */
CREATE DATABASE IF NOT EXISTS fraud_db;
USE fraud_db;


/* ---------- 2. TABLE ----------
   Money columns use DECIMAL (exact), never FLOAT (rounding errors).
   id is an extra surrogate key: the data has no natural unique key. */
CREATE TABLE IF NOT EXISTS transactions (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    step           INT,            -- 1 step = 1 hour (1 to 743)
    type           VARCHAR(20),    -- PAYMENT, TRANSFER, CASH_OUT, CASH_IN, DEBIT
    amount         DECIMAL(18,2),
    nameOrig       VARCHAR(20),    -- sender ID
    oldbalanceOrg  DECIMAL(18,2),  -- sender balance before
    newbalanceOrig DECIMAL(18,2),  -- sender balance after
    nameDest       VARCHAR(20),    -- receiver ID (C = customer, M = merchant)
    oldbalanceDest DECIMAL(18,2),  -- receiver balance before
    newbalanceDest DECIMAL(18,2),  -- receiver balance after
    isFraud        TINYINT,        -- actual label: 1 = fraud
    isFlaggedFraud TINYINT         -- bank's rule-based flag
);


/* ---------- 3. ENABLE LOCAL LOAD ----------
   Needed on the server side (resets after a MySQL restart).
   Client side: in Workbench, Manage Connections > Advanced >
   Others, add the line:  OPT_LOCAL_INFILE=1                    */
SET GLOBAL local_infile = 1;


/* ---------- 4. BULK LOAD (about 3 to 4 minutes) ----------
   '\n' line endings (the file is not '\r\n').
   id is not in the column list: MySQL fills it automatically. */
LOAD DATA LOCAL INFILE 'D:/Data analytics Project/Bank Data set/Fraud.csv'
INTO TABLE fraud_db.transactions
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(step, type, amount, nameOrig, oldbalanceOrg, newbalanceOrig,
 nameDest, oldbalanceDest, newbalanceDest, isFraud, isFlaggedFraud);

/* If a load goes wrong (duplicates or partial data), clear and redo:
   TRUNCATE TABLE fraud_db.transactions;                          */


/* ---------- 5. VERIFY THE LOAD ---------- */
-- Expected: 6,362,620
SELECT COUNT(*) AS total_rows
FROM fraud_db.transactions;

-- Fraud vs non-fraud. Expected: 0 -> 6,354,407 | 1 -> 8,213
SELECT isFraud, COUNT(*) AS txns
FROM fraud_db.transactions
GROUP BY isFraud;


/* ---------- 6. FRAUD BY TRANSACTION TYPE ---------- */
SELECT type,
       COUNT(*)     AS total_txns,
       SUM(isFraud) AS fraud_txns
FROM fraud_db.transactions
GROUP BY type;
-- Finding: fraud appears only in TRANSFER and CASH_OUT.


/* ---------- 7. BALANCE CHECK (sender side) ----------
   Rule: oldbalanceOrg - amount should equal newbalanceOrig.
   Caveat: this formula is wrong for CASH_IN (money comes in),
   so CASH_IN shows 100% mismatch. A proper validation query
   should handle each type separately (Phase 1, Query 4). */
SELECT COUNT(*) AS mismatch_rows
FROM fraud_db.transactions
WHERE oldbalanceOrg - amount <> newbalanceOrig;
-- Result: 5,125,552 (about 80.6% of all rows)


/* ---------- 8. SUMMARY QUERY ---------- */
SELECT type,
       COUNT(*)                                       AS total_txns,
       SUM(isFraud)                                   AS fraud_txns,
       ROUND(100 * SUM(isFraud) / COUNT(*), 3)        AS fraud_pct,
       SUM(oldbalanceOrg - amount <> newbalanceOrig)  AS mismatch_txns
FROM fraud_db.transactions
GROUP BY type
ORDER BY fraud_txns DESC;

/* Results:
   type      | total_txns | fraud_txns | fraud_pct | mismatch_txns
   CASH_OUT  | 2,237,500  | 4,116      | 0.184     | 1,998,093
   TRANSFER  |   532,909  | 4,097      | 0.769     |   509,628
   PAYMENT   | 2,151,495  | 0          | 0.000     | 1,205,652
   DEBIT     |    41,432  | 0          | 0.000     |    12,895
   CASH_IN   | 1,399,284  | 0          | 0.000     | 1,399,284

   Insights:
   - Fraud occurs only in TRANSFER (0.77%) and CASH_OUT (0.18%).
   - Balance mismatch alone is a weak fraud signal: about 5.1M rows
     mismatch, but only 8,213 are fraud.                          */


/* ---------- TODO (Phase 1, remaining) ----------
   - Data quality: NULL and duplicate checks
   - Indexes (create after loading, not before)
   - Query 1: Recursive fraud chain (money laundering path)
   - Query 2: Rolling fraud sum
   - Query 3: Complex fraud (3 red flags together)
   - Query 4: Balance validation, handled per transaction type
   - 5 custom analysis queries                                     */