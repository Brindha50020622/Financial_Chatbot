import os
import sqlite3
import requests
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import time

# Configuration
API_KEY = "AIzaSyClv_j_tVzI3WUoRPmQvcRjCBizurSVrOA"  # Replace with your actual API key
MAX_RESULTS = 3
THUMBNAIL_DIR = "financial_videos"
os.makedirs(THUMBNAIL_DIR, exist_ok=True)

def setup_database():
    """Initialize database connection"""
    conn = sqlite3.connect('financial_videos.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS financial_videos (
            id INTEGER PRIMARY KEY,
            ticker TEXT NOT NULL,
            company TEXT NOT NULL,
            video_url TEXT NOT NULL UNIQUE,
            source TEXT NOT NULL,
            title TEXT,
            duration TEXT,
            thumbnail_path TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn

def download_thumbnail(url, ticker):
    """Download thumbnail image"""
    try:
        response = requests.get(url, timeout=10)
        path = os.path.join(THUMBNAIL_DIR, f"{ticker}_thumb_{int(datetime.now().timestamp())}.jpg")
        with open(path, 'wb') as f:
            response.raise_for_status()
            f.write(response.content)
        return path
    except Exception as e:
        print(f"Thumbnail download failed: {e}")
        return None

def search_youtube_videos(api_key, query):
    """Search YouTube using official API"""
    youtube = build('youtube', 'v3', developerKey=api_key)
    
    request = youtube.search().list(
        q=query,
        part="snippet",
        type="video",
        maxResults=MAX_RESULTS,
        order="relevance",
        videoDuration="medium",  # Filters out shorts
        publishedAfter=(datetime.now() - timedelta(days=30)).isoformat() + "Z"
    )
    
    response = request.execute()
    return response.get('items', [])

def scrape_with_youtube_api(ticker, company_name):
    """Main scraping function using YouTube API"""
    conn = setup_database()
    videos_added = 0
    
    try:
        # Search for financial news videos
        query = f"{company_name} financial news"
        videos = search_youtube_videos(API_KEY, query)
        
        for video in videos:
            try:
                video_id = video['id']['videoId']
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                
                # Check if video already exists
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 1 FROM financial_videos 
                    WHERE video_url = ? 
                    AND timestamp > datetime('now', '-7 days')
                """, (video_url,))
                if cursor.fetchone():
                    continue
                
                # Get video details
                title = video['snippet']['title']
                thumbnail_url = video['snippet']['thumbnails']['high']['url']
                thumbnail_path = download_thumbnail(thumbnail_url, ticker)
                
                # Get duration (requires second API call)
                youtube = build('youtube', 'v3', developerKey=API_KEY)
                video_response = youtube.videos().list(
                    part="contentDetails",
                    id=video_id
                ).execute()
                duration = video_response['items'][0]['contentDetails']['duration']
                
                # Insert into database
                conn.execute("""
                    INSERT INTO financial_videos 
                    (ticker, company, video_url, source, title, duration, thumbnail_path)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    ticker,
                    company_name,
                    video_url,
                    "YouTube",
                    title,
                    duration,
                    thumbnail_path
                ))
                videos_added += 1
                print(f"✅ Saved: {title}")
                
            except Exception as e:
                print(f"Error processing video: {e}")
                continue
        
        conn.commit()
        print(f"\nAdded {videos_added} new videos to database")
        
    finally:
        conn.close()

if __name__ == "__main__":
    companies = {
        "AAPL": "Apple Inc.",
        "MSFT": "Microsoft Corporation",
        "TSLA": "Tesla Inc.",
        "GOOGL": "Alphabet Inc."
    }
    
    for ticker, name in companies.items():
        print(f"\nScraping videos for {name} ({ticker})...")
        scrape_with_youtube_api(ticker, name)
        time.sleep(1)  # Respect API rate limits