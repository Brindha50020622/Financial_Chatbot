import os
import sqlite3
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime

def initialize_database():
    """Initialize database with proper table structure"""
    conn = sqlite3.connect('financial_images.db')
    cursor = conn.cursor()
    
    # Drop existing table if it has problems
    cursor.execute("DROP TABLE IF EXISTS company_images")
    
    # Create new table with proper schema
    cursor.execute("""
        CREATE TABLE company_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            ticker TEXT NOT NULL,
            image_path TEXT NOT NULL UNIQUE,
            description TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def download_yahoo_chart(ticker):
    """Fetch historical stock data and generate a chart"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1mo")  # Last 1 month

        if hist.empty:
            print(f"❌ No data found for {ticker}")
            return None

        # Plot the stock price chart
        plt.figure(figsize=(8, 5))
        plt.plot(hist.index, hist['Close'], label=f"{ticker} Closing Price", color='blue')
        plt.xlabel("Date")
        plt.ylabel("Price (USD)")
        plt.title(f"{ticker} Stock Price Chart")
        plt.legend()
        plt.grid()

        # Save chart image
        os.makedirs("scraped_images", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{ticker}_chart_{timestamp}.png"
        filepath = os.path.abspath(os.path.join("scraped_images", filename))
        plt.savefig(filepath)
        plt.close()

        return filepath

    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None

def save_to_database(ticker, company, image_path):
    """Save stock chart image to SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect('financial_images.db')
        cursor = conn.cursor()
        
        # Verify image exists
        if not os.path.exists(image_path):
            print(f"Image file not found: {image_path}")
            return False
            
        # Insert record
        cursor.execute("""
            INSERT INTO company_images 
            (company, ticker, image_path, description)
            VALUES (?, ?, ?, ?)
        """, (
            company,
            ticker,
            image_path,
            f"Yahoo Finance chart generated on {datetime.now().strftime('%Y-%m-%d')}"
        ))
        conn.commit()
        return True
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        if conn:
            conn.close()

def scrape_stock_chart(ticker, company):
    """Main function to fetch and store stock charts"""
    print(f"\nProcessing {ticker}...")
    chart_path = download_yahoo_chart(ticker)
    if chart_path:
        if save_to_database(ticker, company, chart_path):
            print(f"✅ Successfully saved chart for {ticker}")
        else:
            print(f"❌ Failed to save chart for {ticker} to database")
            try:
                os.remove(chart_path)
            except:
                pass

if __name__ == "__main__":
    # Initialize database
    initialize_database()
    
    # Process stocks
    stocks = {
        "AAPL": "Apple Inc.",
        "MSFT": "Microsoft Corporation",
        "TSLA": "Tesla Inc."
    }
    
    for ticker, company in stocks.items():
        scrape_stock_chart(ticker, company)
    
    # Verification
    conn = sqlite3.connect('financial_images.db')
    cursor = conn.cursor()
    
    # Count records
    cursor.execute("SELECT COUNT(*) FROM company_images")
    count = cursor.fetchone()[0]
    print(f"\n🟢 Total charts in database: {count}")
    
    # Show sample records
    print("\nSample records:")
    for row in cursor.execute("SELECT ticker, image_path FROM company_images LIMIT 3"):
        print(f"{row[0]}: {row[1]}")
    
    conn.close()