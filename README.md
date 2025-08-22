
# CredTech: Explainable Credit Scoring

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red)
![Scikit-learn](https://img.shields.io/badge/ML-Scikit--learn-orange)
![License](https://img.shields.io/badge/License-MIT-green)

A real-time, explainable credit scoring platform built for the CredTech Hackathon, organized by The Programming Club, IIT Kanpur and powered by Deep Root Investments.

Our system continuously ingests structured & unstructured data, generates dynamic creditworthiness scores, and provides transparent, evidence-backed explanations for every score — empowering analysts, investors, and regulators.

## 🏗️ What We Built
Solution:

📈 Structured ML Model → Predicts credit rating group (High / Medium / Low) from financial ratios

📰 Unstructured NLP → News sentiment analysis (Positive / Neutral / Negative)

🔗 Integration → Combined final score with reasoning shown in a Streamlit dashboard

## 🏗️ Features

- ⚡ Real-time data ingestion (**Alpha Vantage API**)
- 📊 Credit rating prediction (**Ensemble ML, ~82% accuracy**)
- 📰 Sentiment analysis from financial news
- 🎯 Final score adjustment based on sentiment
- 📈 Interactive analyst dashboard with results + explanation


## 📂 Tech Stack

- **🖥️ Backend / ML:** `Python`, `Scikit-learn`, `XGBoost`, `LightGBM`, `joblib`  
- **🎨 Frontend:** `Streamlit`  
- **📊 Data APIs:** `Alpha Vantage` (financials), custom news input  
- **🔍 Explainability:** `SHAP` → Feature contribution breakdowns  


## 📂 Project Structure




![App Screenshot](https://via.placeholder.com/468x300?text=App+Screenshot+Here)

## 🚀 Run Locally

```bash
git clone https://github.com/<your-team>/credtech.git
cd credtech

pip install -r requirements.txt
streamlit run app.py



