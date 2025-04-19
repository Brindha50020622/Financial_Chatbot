import os
import pandas as pd
import sqlite3

# Define the base directory
base_dir = "Data"

# Connect to SQLite Database
conn = sqlite3.connect("financial_data.db")
cursor = conn.cursor()

# Create table if not exists (structured data)
cursor.execute("""
CREATE TABLE IF NOT EXISTS stock_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT,
    company TEXT,
    file_name TEXT,
    date TEXT,  
    open_price REAL,
    high_price REAL,
    low_price REAL,
    close_price REAL,
    volume INTEGER
)
""")
conn.commit()

# Function to load all CSV files in a folder
def load_csv_files(folder_path):
    csv_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".csv"):
                csv_files.append(os.path.join(root, file))
    return csv_files

# Load CSV files
yahoo_csv_files = load_csv_files(os.path.join(base_dir, "Stock_data", "Yahoo"))
alpha_vantage_csv_files = load_csv_files(os.path.join(base_dir, "Stock_data", "alpha vintage"))
annual_report_csv_files = load_csv_files(os.path.join(base_dir, "annual reports"))
sentiment_csv_file = load_csv_files(os.path.join(base_dir, "sentiment"))

# Function to preprocess CSV files
def preprocess_csv(file_path):
    encodings = ['utf-8', 'ISO-8859-1', 'windows-1252', 'utf-16']
    
    for encoding in encodings:
        try:
            df = pd.read_csv(file_path, encoding=encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ValueError(f"Could not read {file_path} with any of the tried encodings: {encodings}")
    
    df.dropna(inplace=True)

    # Convert "Date" column to datetime if available
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], utc=True)

    # Add a stock symbol column
    stock_symbol = os.path.basename(file_path).split(".")[0]
    df["Symbol"] = stock_symbol
    
    return df

# Function to save structured data to SQLite
def save_to_db(df, source, file_name):
    if not df.empty and {"Date", "Open", "High", "Low", "Close", "Volume"}.issubset(df.columns):
        df = df[["Date", "Open", "High", "Low", "Close", "Volume", "Symbol"]].copy()
        df.rename(columns={
            "Date": "date",
            "Open": "open_price",
            "High": "high_price",
            "Low": "low_price",
            "Close": "close_price",
            "Volume": "volume",
            "Symbol": "company"
        }, inplace=True)
        df["source"] = source
        df["file_name"] = file_name
        df.to_sql("stock_data", conn, if_exists="append", index=False)
        print(f"Data from {file_name} saved to SQLite.")
    else:
        print(f"Skipping {file_name}: Missing required columns.")

# Preprocess and save Yahoo data
for file in yahoo_csv_files:
    save_to_db(preprocess_csv(file), "Yahoo", os.path.basename(file))

# Preprocess and save Alpha Vantage data
for file in alpha_vantage_csv_files:
    save_to_db(preprocess_csv(file), "Alpha Vantage", os.path.basename(file))

# Preprocess and save Annual Reports
for file in annual_report_csv_files:
    save_to_db(preprocess_csv(file), "Annual Reports", os.path.basename(file))

# Close SQLite connection
conn.close()

print("All data preprocessed and stored successfully!")
