import pandas as pd
import sqlite3
import os

# Connect to SQLite
conn = sqlite3.connect("financial_data.db")
cursor = conn.cursor()

# Create table for stock prices
cursor.execute("""
CREATE TABLE IF NOT EXISTS alpha_vantage_stock_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT,
    timestamp TEXT,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    volume INTEGER
)
""")
conn.commit()

# Function to store stock price data
def save_stock_prices_to_db(file_path):
    try:
        df = pd.read_csv(file_path, encoding="utf-8")

        # Check if the file contains an error message
        if "Information" in df.columns[0]:  
            print(f"Skipping {file_path} as it contains an Alpha Vantage error message.")
            return

        # Ensure column names match expected format
        df.rename(columns={"Timestamp": "timestamp", "Open": "open", "High": "high", 
                           "Low": "low", "Close": "close", "Volume": "volume"}, inplace=True)
        
        # Convert timestamp to proper format
        df["timestamp"] = pd.to_datetime(df["timestamp"], format="%Y-%m-%d", errors="coerce")
        
        # Drop rows where timestamp is NaT (invalid dates)
        df.dropna(subset=["timestamp"], inplace=True)
        
        # Save to database
        df.to_sql("alpha_vantage_stock_prices", conn, if_exists="append", index=False)
        print(f"Data from {file_path} saved successfully!")

    except Exception as e:
        print(f"Error processing {file_path}: {e}")

# Provide the path to your Alpha Vantage CSV file
alpha_vantage_csv_files = [r"C:\Users\sarat\OneDrive\Documents\Buckman\Data\Stock_data\alpha vintage\selected_stocks_daily_data.csv", r"C:\Users\sarat\OneDrive\Documents\Buckman\Data\Stock_data\alpha vintage\selected_stocks_daily_data_2.csv"]  # Modify with actual file names

for file in alpha_vantage_csv_files:
    if os.path.exists(file):
        save_stock_prices_to_db(file)
    else:
        print(f"File not found: {file}")

# Close connection
conn.close()
