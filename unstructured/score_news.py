import pandas as pd

def calculate_credit_impact(processed_file="processed_news_AAPL.csv"):
    try:
        # Load processed news data
        df = pd.read_csv(processed_file)
        if df.empty:
            print(f"No data in {processed_file}")
            return []

        # Mock scoring: Adjust score based on keywords and sentiment
        results = []
        for index, row in df.iterrows():
            keywords = eval(row["keywords"]) if isinstance(row["keywords"], str) else row["keywords"]
            sentiment = row["sentiment"]
            title = row["title"]

            # Simple scoring logic (adjust as needed)
            score_adjustment = 0
            for keyword, category in keywords:
                if category == "negative":
                    score_adjustment -= 0.1  # Decrease score for negative events
                elif category == "positive":
                    score_adjustment += 0.1  # Increase score for positive events
            if sentiment < 0:
                score_adjustment -= 0.05 * abs(sentiment)  # Penalize negative sentiment
            elif sentiment > 0:
                score_adjustment += 0.05 * sentiment  # Boost for positive sentiment

            results.append({
                "title": title,
                "keywords": keywords,
                "sentiment": sentiment,
                "score_adjustment": round(score_adjustment, 3),
                "explanation": f"Score adjusted by {score_adjustment:.3f} due to keywords {keywords} and sentiment {sentiment}"
            })

        return results
    except Exception as e:
        print(f"Error processing {processed_file}: {e}")
        return []

# Test the scoring
if __name__ == "__main__":
    tickers = ["AAPL", "TSLA"]
    for ticker in tickers:
        print(f"Scoring {ticker}...")
        results = calculate_credit_impact(f"processed_news_{ticker}.csv")
        if results:
            for result in results:
                print(f"Title: {result['title']}")
                print(f"Keywords: {result['keywords']}")
                print(f"Sentiment: {result['sentiment']}")
                print(f"Score Adjustment: {result['score_adjustment']}")
                print(f"Explanation: {result['explanation']}")
                print("---")
        else:
            print(f"No scoring results for {ticker}.")