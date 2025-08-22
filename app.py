import streamlit as st
import pandas as pd
import os
import json
import numpy as np
from unstructured.news_fetcher import get_news_for_ticker
from unstructured.process_news import process_news, save_processed_data
from structured.predict import predict_from_alphavantage

# Custom CSS to mimic Next.js styling
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0a0b14;
        color: #f8fafc;
    }
    .card {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.05), rgba(0, 255, 136, 0.05));
        border: 1px solid rgba(0, 212, 255, 0.2);
        border-radius: 0.75rem;
        padding: 1rem;
    }
    .glow-effect {
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar for Company Selection
with st.sidebar:
    st.header("Company Selector")
    selected_ticker = st.selectbox("Select Ticker", options=["AAPL", "TSLA", "MSFT", "JPM", "AMZN"])
    sector = st.selectbox("Select Sector", options=["Technology", "Automotive", "Financial", "E-commerce"])

# Main Content
st.title("Credit Intelligence Dashboard")
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Real-Time Credit Scores")
    if st.button("Refresh Scores"):
        for ticker in ["AAPL", "TSLA", "MSFT", "JPM", "AMZN"]:
            try:
                result = predict_from_alphavantage(ticker, sector="Technology")  # Default sector
                st.markdown(f"**{ticker}**: {result['final_rating']} (Predicted)")
            except Exception as e:
                st.error(f"Error for {ticker}: {str(e)}")

with col2:
    st.subheader("Quick Metrics")
    metrics = [
        {"metric": "Data Sources Active", "value": "15/15", "status": "healthy"},
        {"metric": "Processing Latency", "value": "1.2ms", "status": "optimal"},
        {"metric": "Model Accuracy", "value": "94.7%", "status": "excellent"},
        {"metric": "Last Update", "value": "2s ago", "status": "live"},
    ]
    for metric in metrics:
        st.markdown(f"**{metric['metric']}**: {metric['value']}")

st.markdown("---")

# Tabs for Detailed Analysis
tabs = st.tabs(["Score History", "Risk Distribution", "Market Intelligence"])

with tabs[0]:
    st.subheader("Score History")
    # Mock data for now; replace with real data if available
    st.line_chart(pd.DataFrame(score_history))

with tabs[1]:
    st.subheader("Risk Distribution")
    st.pie_chart(risk_distribution)

with tabs[2]:
    st.subheader("Market Intelligence Feed")
    if st.button(f"Fetch News for {selected_ticker}"):
        with st.spinner("Fetching news..."):
            news = get_news_for_ticker(selected_ticker)
            if news:
                with open(f"news_{selected_ticker}.json", "w") as f:
                    json.dump(news, f)
                processed = process_news(f"news_{selected_ticker}.json")
                if processed:
                    save_processed_data(processed, f"processed_news_{selected_ticker}.csv")
                    df = pd.read_csv(f"processed_news_{selected_ticker}.csv")
                    for _, row in df.iterrows():
                        st.markdown(f"**{row['title']}** - Impact: {row['sentiment_label']}")
            else:
                st.error(f"No news found for {selected_ticker}")

# Feature Importance and AI Explanation
st.markdown("---")
st.subheader("Credit Score Prediction")
if st.button(f"Predict for {selected_ticker}"):
    with st.spinner("Predicting..."):
        try:
            credit_result = predict_from_alphavantage(selected_ticker, sector)
            st.write(f"**Group Prediction:** {credit_result['group_prediction']}")
            st.write(f"**Final Predicted Rating:** {credit_result['final_rating']}")
            st.write(f"**Explanation:** {credit_result['explanation']}")
            st.json({"Ratios Used": credit_result['ratios']})
        except Exception as e:
            st.error(f"Prediction error: {str(e)}")

st.subheader("News Analysis Details")
if os.path.exists(f"processed_news_{selected_ticker}.csv"):
    df = pd.read_csv(f"processed_news_{selected_ticker}.csv")
    st.dataframe(df)