# unstructured/process_news.py
from .sentiment import analyze_sentiment, detect_risk
import json
import pandas as pd
import os
import time
from spacy.matcher import PhraseMatcher

def load_news(filename):
    try:
        with open(os.path.join("data", filename), "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {os.path.join('data', filename)}: {e}")
        return []

def process_article(article):
    text = article.get("title", "") + " " + article.get("summary", "")
    sentiment = article.get("overall_sentiment_score", 0)
    sentiment_label = analyze_sentiment(text, sentiment)
    risk_factor = detect_risk(text, sentiment)
    return {
        "title": article.get("title", ""),
        "summary": article.get("summary", ""),
        "keywords": [],  # Placeholder—expand if needed
        "phrases": [],   # Placeholder—expand if needed
        "entities": [],  # Placeholder—expand if needed
        "sentiment": sentiment,
        "sentiment_label": sentiment_label,
        "time_published": article.get("time_published", ""),
        "risk_factor": risk_factor
    }

def process_news(filename):
    news = load_news(filename)
    return [process_article(article) for article in news]

def save_processed_data(processed_data, filename):
    try:
        df = pd.DataFrame(processed_data)
        df.to_csv(os.path.join("data", filename), index=False)
        print(f"Saved processed data to {os.path.join('data', filename)}")
    except Exception as e:
        print(f"Error saving CSV: {e}")

if __name__ == "__main__":
    ticker = input("Enter ticker (e.g., TSLA): ")
    filename = f"news_{ticker}.json"
    csv_filename = f"processed_news_{ticker}.csv"
    processed = process_news(filename)
    if processed:
        save_processed_data(processed, csv_filename)