import requests
import json
import time
import os  # New: For checking file timestamps

# Your Alpha Vantage API key
API_KEY = "9CCSXABEO1Q3G1AZ"  # Replace with your key from api_key.txt

def fetch_news(ticker="AAPL", limit=5):
    url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={ticker}&topics=financial&limit={limit}&apikey={API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Check for HTTP errors
        data = response.json()
        if "feed" in data:
            return data["feed"]
        else:
            print(f"No news found for {ticker} or API limit reached.")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news for {ticker}: {e}")
        return []

def save_news(news, filename):
    try:
        with open(filename, "w") as f:
            json.dump(news, f, indent=2)
        print(f"Saved news to {filename}")
    except Exception as e:
        print(f"Error saving news: {e}")

def is_cache_fresh(filename, max_age=3600):  # 1 hour in seconds
    if os.path.exists(filename):
        age = time.time() - os.path.getmtime(filename)
        if age < max_age:
            print(f"{filename} is fresh (age {age:.0f} seconds)")
            return True
    return False

def load_from_cache(filename):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading cache {filename}: {e}")
        return None

def get_news_for_ticker(ticker):
    filename = f"news_{ticker}.json"
    if is_cache_fresh(filename):
        cached_news = load_from_cache(filename)
        if cached_news is not None:
            return cached_news
    news = fetch_news(ticker)
    if news:
        save_news(news, filename)
    return news

# Test: Fetch for a single ticker
if __name__ == "__main__":
    ticker = input("Enter ticker (e.g., AAPL): ")  # For testing
    news = get_news_for_ticker(ticker)
    if news:
        for article in news:
            print(f"Title: {article['title']}")
            print(f"Summary: {article['summary']}")
            print(f"Sentiment: {article['overall_sentiment_score']}")
            print("---")
    else:
        print("No news to show.")
    # Optional: Loop for real-time (uncomment for auto-fetch)
    # while True:
    #     get_news_for_ticker(ticker)
    #     print("Waiting 1 hour...")
    #     time.sleep(3600)