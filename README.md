## 📌 Agenda (TOC Validation)

1. Snowflake Essentials
2. Data Engineering (Load → Transform → Store)
3. Snowpark Basics
4. ML Training (Snowpark ML)
5. Model Registry
6. In-Database Inference
7. Deployment (SQL callable model)

---

## 🔹 Prerequisites

* Snowflake account (Trial is enough)
* Role: `ACCOUNTADMIN` or `SYSADMIN`
* Use **Snowsight UI**
* Use **SQL Worksheet + Python Worksheet**

---

# 1️⃣ Snowflake Setup (SQL)

### Step 1.1 – Use Admin Role

```sql
USE ROLE ACCOUNTADMIN;
```

---

### Step 1.2 – Create Warehouse, Database, Schemas

```sql
CREATE OR REPLACE WAREHOUSE ML_WH
WAREHOUSE_SIZE = 'XSMALL'
AUTO_SUSPEND = 60;

CREATE OR REPLACE DATABASE ML_DB;

CREATE OR REPLACE SCHEMA ML_DB.RAW;
CREATE OR REPLACE SCHEMA ML_DB.PROCESSED;
```

---

### Step 1.3 – Set Context

```sql
USE DATABASE ML_DB;
USE SCHEMA RAW;
USE WAREHOUSE ML_WH;
```

---

# 2️⃣ Data Engineering – Load Data

### Step 2.1 – Create Raw Table

```sql
CREATE OR REPLACE TABLE CUSTOMERS_RAW (
  CUSTOMER_ID INT,
  AGE INT,
  ANNUAL_INCOME INT,
  SPEND INT,
  CHURN INT
);
```

---

### Step 2.2 – Insert Sample Data (No CSV needed)

```sql
INSERT INTO CUSTOMERS_RAW VALUES
(1,25,50000,2000,0),
(2,45,80000,7000,1),
(3,30,60000,3000,0),
(4,50,90000,9000,1);
```

---

### Step 2.3 – Verify Data

```sql
SELECT * FROM CUSTOMERS_RAW;
```

---

# 3️⃣ Snowpark Data Engineering (Python Worksheet)

> Switch to **Python Worksheet**

---

### Step 3.1 – Read Raw Data

```python
df = session.table("ML_DB.RAW.CUSTOMERS_RAW")
df.show()
```

---

### Step 3.2 – Transform Data

```python
df_clean = (
    df.filter(df["AGE"].is_not_null())
      .with_column("ANNUAL_SPEND", df["SPEND"] * 12)
)

df_clean.show()
```

---

### Step 3.3 – Store Processed Data

```python
df_clean.write.mode("overwrite") \
    .save_as_table("ML_DB.PROCESSED.CUSTOMERS_CLEAN")
```

---

# 4️⃣ Feature Engineering (Python)

```python
features = df_clean.select(
    "AGE",
    "ANNUAL_SPEND",
    "CHURN"
)
```

---

# 5️⃣ ML Training (Snowpark ML)

```python
from snowflake.ml.modeling.linear_model import LogisticRegression

model = LogisticRegression(
    input_cols=["AGE", "ANNUAL_SPEND"],
    label_cols="CHURN"
)

model.fit(features)
```

---

# 6️⃣ Model Registry (VERY IMPORTANT)

### Step 6.1 – Register Model

```python
from snowflake.ml.registry import Registry

registry = Registry(session)

registry.log_model(
    model,
    model_name="churn_model",
    version_name="v1"
)
```

---

### Step 6.2 – Verify Model

```python
registry.show_models()
```

Expected:

```
churn_model | v1
```

---

# 7️⃣ Deploy Model as SQL Function

```python
model_ref = registry.get_model("churn_model").version("v1")

model_ref.deploy(
    deployment_name="churn_model_v1",
    target_warehouse="ML_WH"
)
```

---

# 8️⃣ In-Database Inference (SQL)

> Switch to **SQL Worksheet**

---

### Step 8.1 – Verify Function

```sql
SHOW USER FUNCTIONS LIKE '%CHURN%';
```

---

### Step 8.2 – Run Prediction

```sql
SELECT
  AGE,
  ANNUAL_SPEND,
  CHURN_MODEL_V1(AGE, ANNUAL_SPEND) AS PREDICTION
FROM ML_DB.PROCESSED.CUSTOMERS_CLEAN;
```

---

# 9️⃣ Batch Scoring (Optional – For Demo)

```sql
CREATE OR REPLACE TABLE CHURN_PREDICTIONS AS
SELECT
  *,
  CHURN_MODEL_V1(AGE, ANNUAL_SPEND) AS PREDICTION
FROM ML_DB.PROCESSED.CUSTOMERS_CLEAN;
```

---

# 🔍 Debugging Commands (Trainer Safety Net)

```sql
SELECT CURRENT_ROLE();
SHOW TABLES IN SCHEMA ML_DB.PROCESSED;
SHOW USER FUNCTIONS;
```

```python
registry.show_models()
```
