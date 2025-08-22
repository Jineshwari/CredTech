import streamlit as st
import pandas as pd
import os
from unstructured.process_news import process_news, save_processed_data
from unstructured.news_fetcher import get_news_for_ticker
from structured.predict import predict_from_alphavantage
from structured.structured2.data_ingestion import ingest_data_for_issuers
from structured.structured2.scoring_engine import ScoringEngine
from structured.structured2.explainability import generate_explanation
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="CredTech Intelligence",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #0066cc;
        --secondary-color: #00cc99;
        --accent-color: #ff6b35;
        --dark-bg: #0e1117;
        --card-bg: #1a1d29;
        --text-primary: #ffffff;
        --text-secondary: #a0a0a0;
        --success-color: #00ff88;
        --warning-color: #ffaa00;
        --error-color: #ff4444;
    }
    
    /* Hide default streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container styling */
    .main > div {
        padding-top: 0rem;
    }
    
    /* Custom header */
    .custom-header {
        background: linear-gradient(135deg, #0066cc 0%, #00cc99 100%);
        padding: 2rem 1rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0, 102, 204, 0.3);
    }
    
    .header-title {
        color: white;
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .header-subtitle {
        color: rgba(255,255,255,0.9);
        font-size: 1.2rem;
        font-weight: 400;
    }
    
    /* Input section styling */
    .input-section {
        background: linear-gradient(145deg, #1a1d29 0%, #252938 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        border: 1px solid #333;
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
    }
    
    /* Card styling */
    .metric-card {
        background: linear-gradient(145deg, #1a1d29 0%, #252938 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid #333;
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        margin-bottom: 1rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.3);
    }
    
    /* News card styling */
    .news-card {
        background: linear-gradient(145deg, #1a1d29 0%, #252938 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 4px solid #00cc99;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    .news-title {
        color: #00cc99;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .news-summary {
        color: #ffffff;
        margin-bottom: 1rem;
        line-height: 1.6;
    }
    
    .news-meta {
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
        margin-top: 1rem;
    }
    
    .meta-badge {
        background: rgba(0, 204, 153, 0.2);
        color: #00cc99;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    /* Score display */
    .score-display {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(145deg, #1a1d29 0%, #252938 100%);
        border-radius: 15px;
        border: 1px solid #333;
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
    }
    
    .score-number {
        font-size: 4rem;
        font-weight: 700;
        background: linear-gradient(135deg, #00cc99 0%, #0066cc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .score-label {
        color: #a0a0a0;
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }
    
    /* Status indicators */
    .status-high {
        color: #00ff88;
        background: rgba(0, 255, 136, 0.1);
        padding: 0.5rem 1rem;
        border-radius: 25px;
        border: 1px solid #00ff88;
    }
    
    .status-medium {
        color: #ffaa00;
        background: rgba(255, 170, 0, 0.1);
        padding: 0.5rem 1rem;
        border-radius: 25px;
        border: 1px solid #ffaa00;
    }
    
    .status-low {
        color: #ff4444;
        background: rgba(255, 68, 68, 0.1);
        padding: 0.5rem 1rem;
        border-radius: 25px;
        border: 1px solid #ff4444;
    }
    
    /* Custom button styling */
    .stButton > button {
        background: linear-gradient(135deg, #0066cc 0%, #00cc99 100%);
        color: white;
        border: none;
        padding: 0.8rem 2rem;
        border-radius: 25px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(0, 102, 204, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 102, 204, 0.6);
    }
    
    /* Professional header section */
    .control-panel {
        background: linear-gradient(145deg, #1a1d29 0%, #252938 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        border: 1px solid #333;
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
    }
    
    .control-header {
        color: #00cc99;
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
        text-align: center;
        border-bottom: 1px solid #333;
        padding-bottom: 1rem;
    }
    
    /* Animation classes */
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .slide-in {
        animation: slideInUp 0.6s ease-out;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .header-title {
            font-size: 2rem;
        }
        
        .score-number {
            font-size: 3rem;
        }
        
        .news-meta {
            flex-direction: column;
        }
    }
</style>
""", unsafe_allow_html=True)

# Custom header
st.markdown("""
<div class="custom-header">
    <div class="header-title">🏦 CredTech Intelligence</div>
    <div class="header-subtitle">Advanced Credit Risk Analysis & Market Intelligence Platform</div>
</div>
""", unsafe_allow_html=True)

# Professional control panel
st.markdown("""
<div class="control-panel">
    <div class="control-header">🎯 Company Analysis Dashboard</div>
</div>
""", unsafe_allow_html=True)

# Input section - now full width and more professional
input_col1, input_col2, input_col3 = st.columns([3, 2, 2])

with input_col1:
    ticker = st.text_input(
        "🏢 Stock Ticker Symbol", 
        value="AAPL",
        placeholder="Enter ticker symbol (e.g., AAPL, TSLA, MSFT)",
        help="Enter the stock ticker symbol for comprehensive analysis"
    ).upper()

with input_col2:
    sector = st.text_input(
        "🏭 Industry Sector", 
        value="TECHNOLOGY",
        placeholder="Enter company sector",
        help="Specify the industry sector for enhanced analysis accuracy"
    )

with input_col3:
    st.markdown("<br>", unsafe_allow_html=True)  # Add spacing
    analyze_btn = st.button("🔍 Run Complete Analysis", type="primary", use_container_width=True)

if analyze_btn:
    # Progress indicator
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    with st.spinner("🔄 Initializing analysis pipeline..."):
        progress_bar.progress(10)
        status_text.text("Fetching market data...")
        
        # Create main analytics dashboard
        st.markdown("---")
        st.markdown("## 📊 Comprehensive Analysis Dashboard")
        
        # Top-level metrics overview
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        
        # Initialize metrics placeholders
        with metric_col1:
            st.markdown("""
            <div class="metric-card" style="text-align: center;">
                <h4 style="color: #00cc99;">📰 News Sentiment</h4>
                <div id="news-sentiment" style="font-size: 1.5rem; color: #ffffff;">Processing...</div>
            </div>
            """, unsafe_allow_html=True)
        
        with metric_col2:
            st.markdown("""
            <div class="metric-card" style="text-align: center;">
                <h4 style="color: #00cc99;">⭐ Credit Rating</h4>
                <div id="credit-rating" style="font-size: 1.5rem; color: #ffffff;">Analyzing...</div>
            </div>
            """, unsafe_allow_html=True)
        
        with metric_col3:
            st.markdown("""
            <div class="metric-card" style="text-align: center;">
                <h4 style="color: #00cc99;">🎯 Risk Score</h4>
                <div id="risk-score" style="font-size: 1.5rem; color: #ffffff;">Computing...</div>
            </div>
            """, unsafe_allow_html=True)
        
        with metric_col4:
            st.markdown("""
            <div class="metric-card" style="text-align: center;">
                <h4 style="color: #00cc99;">📈 Price Trend</h4>
                <div id="price-trend" style="font-size: 1.5rem; color: #ffffff;">Loading...</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Main analysis sections
        analysis_col1, analysis_col2 = st.columns([3, 2])
        
        with analysis_col1:
            st.markdown("## 📈 Detailed Analysis")
            
            # News Analysis Section
            progress_bar.progress(30)
            status_text.text("Processing news and sentiment...")
            
            with st.expander("📰 News & Market Sentiment", expanded=True):
                news = get_news_for_ticker(ticker)
                if not news:
                    st.error("❌ No news found for the ticker or API limit reached.")
                else:
                    processed = process_news(f"news_{ticker}.json")
                    if processed:
                        save_processed_data(processed, f"processed_news_{ticker}.csv")
                        st.success(f"✅ Successfully processed news for {ticker}")
                        
                        news_results = []
                        filename = os.path.join("data", f"processed_news_{ticker}.csv")
                        if os.path.exists(filename):
                            df = pd.read_csv(filename)
                            news_results = df.to_dict("records")
                        
                        if news_results:
                            for i, item in enumerate(news_results[:3]):  # Show top 3 news
                                sentiment_color = "#00ff88" if float(item['sentiment']) > 0 else "#ff4444" if float(item['sentiment']) < 0 else "#ffaa00"
                                
                                st.markdown(f"""
                                <div class="news-card slide-in">
                                    <div class="news-title">{item['title']}</div>
                                    <div class="news-summary">{item['summary']}</div>
                                    <div class="news-meta">
                                        <span class="meta-badge" style="background: rgba({sentiment_color[1:3]}, {sentiment_color[3:5]}, {sentiment_color[5:7]}, 0.2); color: {sentiment_color};">
                                            📊 Sentiment: {float(item['sentiment']):.2f}
                                        </span>
                                        <span class="meta-badge">🏷️ {item['sentiment_label']}</span>
                                        <span class="meta-badge">⚠️ Risk: {item['risk_factor']}</span>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.warning("⚠️ No processed news data available.")
            
            # Credit Rating Prediction
            progress_bar.progress(60)
            status_text.text("Running credit rating models...")
            
            with st.expander("🎯 Credit Rating Prediction", expanded=True):
                try:
                    result = predict_from_alphavantage(ticker, sector)
                    
                    # Create metrics display
                    met_col1, met_col2 = st.columns(2)
                    
                    with met_col1:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h3 style="color: #00cc99;">📊 Group Prediction</h3>
                            <div style="font-size: 2rem; font-weight: 700; color: #ffffff;">
                                {result['group_prediction']}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with met_col2:
                        rating_color = "#00ff88" if result['final_rating'] in ['AAA', 'AA', 'A'] else "#ffaa00" if result['final_rating'] in ['BBB', 'BB'] else "#ff4444"
                        st.markdown(f"""
                        <div class="metric-card">
                            <h3 style="color: #00cc99;">⭐ Final Rating</h3>
                            <div style="font-size: 2rem; font-weight: 700; color: {rating_color};">
                                {result['final_rating']}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4 style="color: #00cc99;">💡 Analysis Explanation</h4>
                        <p style="color: #ffffff; line-height: 1.6;">{result['explanation']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Financial ratios in a nice format
                    st.markdown("### 📊 Key Financial Ratios")
                    ratio_cols = st.columns(len(result['ratios']))
                    for i, (ratio, value) in enumerate(result['ratios'].items()):
                        with ratio_cols[i]:
                            st.metric(
                                label=ratio.replace('_', ' ').title(),
                                value=f"{value:.2f}" if isinstance(value, (int, float)) else str(value)
                            )
                
                except Exception as e:
                    st.error(f"❌ Credit rating prediction failed: {e}")
        
        with analysis_col2:
            st.markdown("## 🎯 Real-time Metrics")
            
            # Enhanced credit score display
            st.markdown("### 🌟 Advanced Credit Scoring")
            
            issuers = [ticker]
            try:
                data = ingest_data_for_issuers(issuers)
                if not data or ticker not in data:
                    st.markdown("""
                    <div class="metric-card" style="text-align: center;">
                        <div style="color: #ffaa00; font-size: 1.2rem;">⚠️ No Data Available</div>
                        <p style="color: #a0a0a0; font-size: 0.9rem;">Structure2 data not found for this ticker</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    features_df = data[ticker]
                    expected_features = ['debt_to_equity', 'current_ratio', 'profit_margin', 'roa', 'price_volatility', 'macro_interest_rate']
                    new_X = features_df[expected_features].iloc[0].to_frame().T
                    engine = ScoringEngine()
                    new_y = [75]
                    engine.retrain(new_X, new_y)
                    score = engine.predict(new_X)
                    
                    # Professional credit score display
                    score_color = "#00ff88" if score >= 80 else "#ffaa00" if score >= 60 else "#ff4444"
                    risk_level = "LOW RISK" if score >= 80 else "MEDIUM RISK" if score >= 60 else "HIGH RISK"
                    
                    st.markdown(f"""
                    <div class="score-display">
                        <div style="color: #00cc99; font-size: 1rem; margin-bottom: 0.5rem;">CREDIT ASSESSMENT</div>
                        <div class="score-number" style="color: {score_color}; font-size: 3.5rem;">{score:.0f}</div>
                        <div style="color: {score_color}; font-size: 1rem; font-weight: 600; margin-top: 0.5rem;">{risk_level}</div>
                        <div class="score-label">Credit Score Rating</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Risk management alerts
                    if score < 60:
                        st.markdown("""
                        <div style="background: rgba(255, 68, 68, 0.1); border: 1px solid #ff4444; 
                                    border-radius: 10px; padding: 1rem; margin: 1rem 0;">
                            <h4 style="color: #ff4444; margin: 0;">🚨 CRITICAL ALERT</h4>
                            <p style="color: #ffffff; margin: 0.5rem 0; font-size: 0.9rem;">
                                Elevated risk detected. Immediate portfolio review recommended.
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                    elif score < 80:
                        st.markdown("""
                        <div style="background: rgba(255, 170, 0, 0.1); border: 1px solid #ffaa00; 
                                    border-radius: 10px; padding: 1rem; margin: 1rem 0;">
                            <h4 style="color: #ffaa00; margin: 0;">⚠️ MONITOR</h4>
                            <p style="color: #ffffff; margin: 0.5rem 0; font-size: 0.9rem;">
                                Moderate risk levels. Continue monitoring key metrics.
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Key financial indicators
                    st.markdown("### 📊 Key Indicators")
                    indicators_data = new_X.iloc[0].to_dict()
                    
                    for feature, value in list(indicators_data.items())[:4]:  # Show top 4 indicators
                        formatted_name = feature.replace('_', ' ').title()
                        st.metric(
                            label=formatted_name,
                            value=f"{value:.3f}",
                            delta=None
                        )
            
            except Exception as e:
                st.markdown(f"""
                <div class="metric-card" style="text-align: center;">
                    <div style="color: #ff4444; font-size: 1.2rem;">❌ Analysis Error</div>
                    <p style="color: #a0a0a0; font-size: 0.9rem;">{str(e)}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Stock price information
            structured_file = os.path.join("data", f"structured_data_{ticker}.csv")
            if os.path.exists(structured_file):
                df_structured = pd.read_csv(structured_file)
                
                if 'close' in df_structured.columns:
                    st.markdown("### 💰 Market Performance")
                    latest_close = df_structured['close'].iloc[-1]
                    prev_close = df_structured['close'].iloc[-2] if len(df_structured) > 1 else latest_close
                    change = latest_close - prev_close
                    change_pct = (change / prev_close) * 100 if prev_close != 0 else 0
                    trend_color = "#00ff88" if change >= 0 else "#ff4444"
                    trend_icon = "📈" if change >= 0 else "📉"
                    
                    st.markdown(f"""
                    <div class="metric-card" style="text-align: center;">
                        <div style="color: #00cc99; font-size: 1rem; margin-bottom: 1rem;">CURRENT PRICE</div>
                        <div style="font-size: 2.5rem; font-weight: 700; color: #ffffff;">${latest_close:.2f}</div>
                        <div style="color: {trend_color}; font-size: 1rem; margin-top: 0.5rem;">
                            {trend_icon} {change:+.2f} ({change_pct:+.2f}%)
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        progress_bar.progress(100)
        status_text.text("✅ Analysis complete!")
        
        # Advanced visualizations section
        st.markdown("## 📊 Advanced Analytics")
        
        viz_col1, viz_col2 = st.columns(2)
        
        with viz_col1:
            try:
                if 'data' in locals() and ticker in data:
                    importances = engine.get_feature_importances(new_X)
                    
                    # Create modern feature importance chart
                    fig_importance = go.Figure(data=[
                        go.Bar(
                            x=list(importances.values()),
                            y=list(importances.keys()),
                            orientation='h',
                            marker=dict(
                                color=list(importances.values()),
                                colorscale='Viridis',
                                colorbar=dict(title="Importance")
                            )
                        )
                    ])
                    
                    fig_importance.update_layout(
                        title=f"📊 Feature Importance Analysis - {ticker}",
                        xaxis_title="Importance Score",
                        yaxis_title="Financial Metrics",
                        template="plotly_dark",
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="white")
                    )
                    
                    st.plotly_chart(fig_importance, use_container_width=True)
            except:
                st.info("📊 Feature importance chart will display after successful analysis")
        
        with viz_col2:
            try:
                if 'data' in locals() and ticker in data:
                    # Score trend visualization
                    today = datetime.now().date()
                    start_date = today - timedelta(days=30)
                    prices = features_df.iloc[0]['close_prices'] if 'close_prices' in features_df.columns else {}
                    price_dates = [d for d in prices.keys() if start_date <= d.date() <= today]
                    price_values = [prices[d] for d in price_dates]
                    
                    if price_values:
                        base_score = score
                        trend_scores = [base_score + (p - price_values[0]) / price_values[0] * 20 for p in price_values]
                        trend_scores = [max(0, min(100, s)) for s in trend_scores]
                        
                        fig_trend = go.Figure()
                        fig_trend.add_trace(go.Scatter(
                            x=price_dates,
                            y=trend_scores,
                            mode='lines+markers',
                            name='Credit Score',
                            line=dict(color='#00cc99', width=3),
                            marker=dict(size=6, color='#00cc99')
                        ))
                        
                        fig_trend.update_layout(
                            title=f"📈 Credit Score Trend - {ticker}",
                            xaxis_title="Date",
                            yaxis_title="Credit Score",
                            template="plotly_dark",
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            font=dict(color="white")
                        )
                        
                        st.plotly_chart(fig_trend, use_container_width=True)
            except:
                st.info("📈 Trend chart will display after successful analysis")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; color: #a0a0a0;">
    <p>🏦 <strong>CredTech Intelligence</strong> | Powered by Advanced AI & Machine Learning</p>
    <p>Real-time credit risk analysis with market intelligence integration</p>
</div>
""", unsafe_allow_html=True)