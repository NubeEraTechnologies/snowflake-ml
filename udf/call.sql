SELECT
  AGE,
  ANNUAL_SPEND,
  customer_risk(AGE, ANNUAL_SPEND) AS risk_level
FROM ml_db.processed.customers_clean;
