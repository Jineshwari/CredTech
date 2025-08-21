import streamlit as st
import pandas as pd
import os
from unstructured.process_news import process_news, save_processed_data
from unstructured.news_fetcher import get_news_for_ticker  # Adjust if function name differs

def query_opensearch(ticker):
    filename = os.path.join("data", f"processed_news_{ticker}.csv")
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        return df.to_dict("records")
    return []

# Streamlit app
st.title("Credit Intelligence Dashboard")
st.write("Enter a ticker to fetch and analyze news in real-time (OpenSearch pending teammate setup)")

# Ticker input
ticker = st.text_input("Enter ticker (e.g., AAPL, TSLA):", "UNH").upper()
if st.button("Fetch and Analyze"):
    with st.spinner("Fetching news..."):
        # Fetch and process news
        news = get_news_for_ticker(ticker)
        if not news:
            st.error(f"No news found for {ticker} or API limit reached.")
        else:
            processed = process_news(f"news_{ticker}.json")
            if processed:
                save_processed_data(processed, f"processed_news_{ticker}.csv")
                st.success(f"Processed news for {ticker}")
                
                # Query OpenSearch (mocked for now)
                news_results = query_opensearch(ticker)
                if news_results:
                    st.subheader(f"News Analysis for {ticker}")
                    for item in news_results:
                        st.write(f"**Title:** {item['title']}")
                        st.write(f"**Summary:** {item['summary']}")
                        st.write(f"**Sentiment:** {item['sentiment']} ({item['sentiment_label']})")
                        st.write(f"**Risk Factor:** {item['risk_factor']}")
                        st.write(f"**Keywords:** {eval(item['keywords']) if item['keywords'] else []}")
                        st.write(f"**Phrases:** {eval(item['phrases']) if item['phrases'] else []}")
                        st.write(f"**Entities:** {eval(item['entities']) if item['entities'] else []}")
                        st.write("---")

                    # Sentiment trend visualization
                    if len(news_results) > 1:
                        st.subheader("Sentiment Trend Visualization")
                        labels = [f"Article {i+1}" for i in range(len(news_results))]
                        sentiments = [item['sentiment'] for item in news_results]
                        st.write("Confirm to generate a chart of sentiment trends?")
                        if st.button("Yes"):
                            st.code("""
                            {
                                "type": "line",
                                "data": {
                                    "labels": [""", ", ".join([f"'{label}'" for label in labels]), """],
                                    "datasets": [{
                                        "label": "Sentiment",
                                        "data": [""", ", ".join([str(s) for s in sentiments]), """],
                                        "backgroundColor": "rgba(75, 192, 192, 0.2)",
                                        "borderColor": "rgba(75, 192, 192, 1)",
                                        "borderWidth": 2
                                    }]
                                },
                                "options": {
                                    "scales": {
                                        "y": {
                                            "beginAtZero": true,
                                            "title": {
                                                "display": true,
                                                "text": "Sentiment Score"
                                            }
                                        },
                                        "x": {
                                            "title": {
                                                "display": true,
                                                "text": "Articles"
                                            }
                                        }
                                     }
                                }
                            }
                            """, language="chartjs")
                else:
                    st.error(f"No data found for {ticker} in OpenSearch mock.")
            else:
                st.error(f"Failed to process news for {ticker}.")

st.subheader("Combined Scoring dfgipdfpgndmf(Coming Soon)")
st.write("Will display risk factor + price trend analysis once fully integrated.")
#import streamlit as st
#import pandas as pd
#import os
#from fetch_news import get_news_for_ticker
#from process_news import process_news, save_processed_data
#
## Placeholder for OpenSearch (replace with real connection when teammate provides)
#def query_opensearch(ticker):
#    # Mock: Load from CSV as fallback
#    filename = f"processed_news_{ticker}.csv"
#    if os.path.exists(filename):
#        df = pd.read_csv(filename)
#        return df.to_dict("records")
#    return []
#
## Streamlit app
#st.title("Credit Intelligence Dashboard")
#st.write("Enter a ticker to fetch and analyze news in real-time (OpenSearch pending teammate setup)")
#
## Ticker input
#ticker = st.text_input("Enter ticker (e.g., AAPL, TSLA):", "UNH").upper()
#if st.button("Fetch and Analyze"):
#    with st.spinner("Fetching news..."):
#        # Fetch and process news
#        news = get_news_for_ticker(ticker)
#        if not news:
#            st.error(f"No news found for {ticker} or API limit reached.")
#        else:
#            processed = process_news(f"news_{ticker}.json")
#            if processed:
#                save_processed_data(processed, f"processed_news_{ticker}.csv")
#                st.success(f"Processed news for {ticker}")
#                
#                # Query OpenSearch (mocked for now)
#                news_results = query_opensearch(ticker)
#                if news_results:
#                    st.subheader(f"News Analysis for {ticker}")
#                    for item in news_results:
#                        st.write(f"**Title:** {item['title']}")
#                        st.write(f"**Summary:** {item['summary']}")
#                        st.write(f"**Sentiment:** {item['sentiment']} ({item['sentiment_label']})")
#                        st.write(f"**Risk Factor:** {item['risk_factor']}")
#                        st.write(f"**Keywords:** {eval(item['keywords']) if item['keywords'] else []}")
#                        st.write(f"**Phrases:** {eval(item['phrases']) if item['phrases'] else []}")
#                        st.write(f"**Entities:** {eval(item['entities']) if item['entities'] else []}")
#                        st.write("---")
#
#                # Load structured data
#                structured_file = f"structured_data_{ticker}.csv"
#                if os.path.exists(structured_file):
#                    df_structured = pd.read_csv(structured_file)
#                    st.subheader(f"Stock Data for {ticker}")
#                    st.write(df_structured)
#                    latest_close = df_structured['close'].iloc[-1]
#                    prev_close = df_structured['close'].iloc[-2] if len(df_structured) > 1 else latest_close
#                    trend = "down" if latest_close < prev_close else "up"
#                    st.write(f"**Trend:** Price is {trend} ({prev_close} to {latest_close})")
#                else:
#                    st.warning(f"No structured data for {ticker}. Add {structured_file}.")
#
#st.subheader("Combined Scoring (Coming Soon)")
#st.write("Will display risk factor + price trend analysis once fully integrated.")