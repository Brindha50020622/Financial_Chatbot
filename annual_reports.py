import pandas as pd
import sqlite3
import os

# Connect to SQLite
conn = sqlite3.connect("financial_data.db")
cursor = conn.cursor()

# Drop existing table to avoid conflicts
cursor.execute("DROP TABLE IF EXISTS company_metrics")

# Recreate the table with cleaned column names
cursor.execute("""
CREATE TABLE company_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER,
    company TEXT,
    category TEXT,
    market_cap_b_usd REAL,
    revenue REAL,
    gross_profit REAL,
    net_income REAL,
    earning_per_share REAL,
    ebitda REAL,
    share_holder_equity REAL,
    cash_flow_operating REAL,
    cash_flow_investing REAL,
    cash_flow_financial REAL,
    current_ratio REAL,
    debt_equity_ratio REAL,
    roe REAL,
    roa REAL,
    roi REAL,
    net_profit_margin REAL,
    free_cash_flow_per_share REAL,
    return_on_tangible_equity REAL,
    number_of_employees INTEGER,
    inflation_rate_us REAL
)
""")
conn.commit()

# Function to clean column names and insert into the database
def save_company_metrics(file_path):
    try:
        df = pd.read_csv(file_path)

        # Rename columns to be SQLite-compatible
        column_mapping = {
            "Market Cap(in B USD)": "market_cap_b_usd",
            "Cash Flow from Operating": "cash_flow_operating",
            "Cash Flow from Investing": "cash_flow_investing",
            "Cash Flow from Financial Activities": "cash_flow_financial",
            "Debt/Equity Ratio": "debt_equity_ratio",
            "Net Profit Margin": "net_profit_margin",
            "Free Cash flow per Share": "free_cash_flow_per_share",
            "Return on Tangible Equity": "return_on_tangible_equity",
            "Number of Employees": "number_of_employees",
            "Inflation Rate(in US)": "inflation_rate_us"
        }

        # Apply column renaming
        df.rename(columns=column_mapping, inplace=True)

        # Standardize column names: lowercase, replace spaces with underscores
        df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

        # Save to database
        df.to_sql("company_metrics", conn, if_exists="append", index=False)
        print(f"Company metrics from {file_path} saved successfully!")

    except Exception as e:
        print(f"Error processing {file_path}: {e}")

# File path
company_metrics_file = r"C:\Users\sarat\OneDrive\Documents\Buckman\Data\annual reports\Financial Statements.csv"