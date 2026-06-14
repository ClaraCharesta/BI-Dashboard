import sys
import os
import pandas as pd
import sqlalchemy
from sqlalchemy import text

# =========================
# PATH SETUP
# =========================
sys.path.append(os.path.abspath("."))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.mysql_connection import get_engine

engine = get_engine()

# =========================
# DISABLE FOREIGN KEY CHECK
# =========================
with engine.begin() as conn:
    conn.execute(text("SET FOREIGN_KEY_CHECKS=0"))

print("🔧 FK CHECK DISABLED")

# =========================
# LOAD CSV
# =========================
dim_cause = pd.read_csv("data/dim_cause.csv")
dim_type = pd.read_csv("data/dim_type.csv")
dim_year = pd.read_csv("data/dim_year.csv")
dim_source = pd.read_csv("data/dim_source.csv")
fact_deaths = pd.read_csv("data/fact_deaths.csv")

print("📥 CSV LOADED")

# =========================
# CLEAN COLUMN (optional safety)
# =========================
dim_cause.columns = dim_cause.columns.str.strip()
fact_deaths.columns = fact_deaths.columns.str.strip()

# =========================
# LOAD DIM TABLES
# =========================

# ---- dim_cause (WITH PRIMARY KEY) ----
dim_cause.to_sql(
    "dim_cause",
    engine,
    if_exists="replace",
    index=False,
    dtype={
        "cause_id": sqlalchemy.types.BigInteger(),
        "cause_name": sqlalchemy.types.Text()
    }
)

with engine.begin() as conn:
    conn.execute(text("""
        ALTER TABLE dim_cause
        ADD PRIMARY KEY (cause_id)
    """))

print("✅ dim_cause loaded")

# ---- other dimensions ----
dim_type.to_sql("dim_type", engine, if_exists="replace", index=False)
dim_year.to_sql("dim_year", engine, if_exists="replace", index=False)
dim_source.to_sql("dim_source", engine, if_exists="replace", index=False)

print("✅ other dims loaded")

# =========================
# VALIDATE FACT (IMPORTANT!)
# =========================

missing_fk = fact_deaths[~fact_deaths["cause_id"].isin(dim_cause["cause_id"])]

print(f"⚠️ Missing FK rows: {len(missing_fk)}")

if len(missing_fk) > 0:
    print("❌ Sample invalid FK data:")
    print(missing_fk.head())

    # auto clean biar tidak error
    fact_deaths = fact_deaths[
        fact_deaths["cause_id"].isin(dim_cause["cause_id"])
    ]

    print("🧹 Fact cleaned (invalid FK removed)")

# =========================
# LOAD FACT TABLE
# =========================

fact_deaths.to_sql(
    "fact_deaths",
    engine,
    if_exists="replace",
    index=False,
    dtype={
        "cause_id": sqlalchemy.types.BigInteger()
    }
)

print("✅ fact_deaths loaded")

# =========================
# ADD FOREIGN KEY
# =========================

with engine.begin() as conn:
    conn.execute(text("""
        ALTER TABLE fact_deaths
        ADD CONSTRAINT fk_cause
        FOREIGN KEY (cause_id)
        REFERENCES dim_cause(cause_id)
    """))

print("🔗 FK constraint added")

# =========================
# ENABLE FK CHECK
# =========================

with engine.begin() as conn:
    conn.execute(text("SET FOREIGN_KEY_CHECKS=1"))

print("🔓 FK CHECK ENABLED")

# =========================
# DONE
# =========================

print("🚀 ETL PHASE 3 BERHASIL SELESAI!")