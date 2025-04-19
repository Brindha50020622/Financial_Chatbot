# FINANCIAL DATA ASSISTANT(RAG based chatbot )

This project collects, organizes, and analyzes financial data for major companies (like Apple, Microsoft, Tesla, etc.) to help users get stock information, financial reports, and related videos.

1. Data Collection

    •	Stock Prices: Gathers daily stock data (open/close prices, volume) from:
   
        o	Yahoo Finance(had 30+ companies stock details)
   
        o	Alpha Vantage API
   
    •	Company Metrics: Stores financial health indicators like:
   
        o	Revenue
   
        o	 Profit margins
   
        o	Debt ratios
   
        o	Employee counts
   
   •	Financial Reports: Extracts text from:
   
        o	PDF annual reports
   
        o	Word documents
   
        o	HTML filings
   
   •	Videos: Finds relevant financial news videos from YouTube(web scraped).
   
   •	Images: Web scraped from finance and stock websites.

2. Data Storage
   
All information is saved in an SQLite database (financial_data.db,financial_images.db,financial_videos.db) with these tables:

    •	stock_data - Daily price history

    •	company_metrics - Financial health indicators

    •	financial_reports - Extracted document text

    •	company_videos - Links to relevant videos

    •	company_images- image storage 

3.Data Processing Pipeline

Key Steps:

1.	Data Ingestion
   
        o	CSV files (stock data, company metrics) → Pandas for cleaning
  	
        o	PDFs /DOCs/HTML → PyMuPDF, python-docx, BeautifulSoup for text extraction
  	
        o	YouTube API → Fetches latest financial videos
  	
2.	Data Cleaning & Transformation

        o	Handling different encodings (UTF-8, ISO-8859-1, etc.)
  	
        o	Date standardization (converting to YYYY-MM-DD)
  	
        o	Dropping invalid rows (missing dates, corrupted files)
  	
3.	Database Storage

        o	SQLite for lightweight, file-based storage
  	
        o	pandas.to_sql() for bulk inserts
  	
        o	Error handling for duplicate entries


4.Backend: Retrieval & Response Generation

FinancialRetriever Class

    •	Normalizes company names (e.g., "Apple Inc." → "AAPL")
    
    •	SQL queries to fetch:
    
          o	Stock prices (latest 30 days)
          
          o	Financial reports (with text summaries)
          
          o	YouTube videos (filtered by relevance)
          
ResponseGenerator Class

    •	Determines user intent (stock price vs. reports vs. videos)
    
    •	Formats responses in a readable way (Markdown-style)

5.Tech Stack

    •	Gradio (for quick web UI)
    
    •	Logging (tracks errors, user queries)

   

