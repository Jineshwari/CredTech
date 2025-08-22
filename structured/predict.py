import joblib
import pandas as pd
from alpha_vantage.fundamentaldata import FundamentalData
import os, json, numpy as np

# ------------------------------
# Load model artifacts
# ------------------------------
BASE_DIR = os.path.dirname(__file__)   # folder where predict.py is located
rf_model = joblib.load(os.path.join(BASE_DIR, "credit_rf_model.joblib"))
preprocessor = joblib.load(os.path.join(BASE_DIR, "preprocessor.joblib"))
le = joblib.load(os.path.join(BASE_DIR, "label_encoder.joblib"))

with open(os.path.join(BASE_DIR, "group_label_distribution.json"), "r") as f:
    group_to_original = json.load(f)

# ensure all probs are floats (in case JSON saved as strings)
for g, mapping in group_to_original.items():
    group_to_original[g] = {k: float(v) for k, v in mapping.items()}

# ------------------------------
# Alpha Vantage setup
# ------------------------------
API_KEY = "WY9FJNSAA8LNT50H"   # replace with your real key
fd = FundamentalData(key=API_KEY, output_format="pandas")

# ------------------------------
# Safe converter
# ------------------------------
def safe_float(x):
    try:
        if x in [None, "None", "NaN", "nan", ""]:
            return 0.0
        return float(x)
    except Exception:
        return 0.0

# ------------------------------
# Compute ratios from AV data
# ------------------------------
def compute_ratios_from_av(bs, is_, cf, sector="TECHNOLOGY"):
    bs0, is0, cf0 = bs.iloc[0], is_.iloc[0], cf.iloc[0]

    total_assets = safe_float(bs0.get("totalAssets"))
    total_liab = safe_float(bs0.get("totalLiabilities"))
    current_assets = safe_float(bs0.get("totalCurrentAssets"))
    current_liab = safe_float(bs0.get("totalCurrentLiabilities"))
    long_term_debt = safe_float(bs0.get("longTermDebtNoncurrent"))
    total_equity = safe_float(bs0.get("totalShareholderEquity"))
    shares_out = safe_float(bs0.get("commonStockSharesOutstanding"))

    revenue = safe_float(is0.get("totalRevenue"))
    gross_profit = safe_float(is0.get("grossProfit"))
    ebit = safe_float(is0.get("ebit"))
    net_income = safe_float(is0.get("netIncome"))
    pretax_income = safe_float(is0.get("incomeBeforeTax"))
    operating_income = safe_float(is0.get("operatingIncome"))

    op_cf = safe_float(cf0.get("operatingCashflow"))
    capex = safe_float(cf0.get("capitalExpenditures"))
    free_cf = op_cf + capex  # capex is negative

    return {
        "Sector": sector,
        "Current Ratio": current_assets / current_liab if current_liab else 0,
        "Long-term Debt / Capital": long_term_debt / (long_term_debt + total_equity) if (long_term_debt + total_equity) else 0,
        "Debt/Equity Ratio": total_liab / total_equity if total_equity else 0,
        "Gross Margin": gross_profit / revenue if revenue else 0,
        "Operating Margin": operating_income / revenue if revenue else 0,
        "EBIT Margin": ebit / revenue if revenue else 0,
        "Pre-Tax Profit Margin": pretax_income / revenue if revenue else 0,
        "Net Profit Margin": net_income / revenue if revenue else 0,
        "Asset Turnover": revenue / total_assets if total_assets else 0,
        "ROE - Return On Equity": net_income / total_equity if total_equity else 0,
        "ROA - Return On Assets": net_income / total_assets if total_assets else 0,
        "Operating Cash Flow Per Share": op_cf / shares_out if shares_out else 0,
        "Free Cash Flow Per Share": free_cf / shares_out if shares_out else 0
    }

# ------------------------------
# Predict from Alpha Vantage
# ------------------------------
def predict_from_alphavantage(ticker, sector="TECHNOLOGY"):
    bs, _ = fd.get_balance_sheet_annual(ticker)
    is_, _ = fd.get_income_statement_annual(ticker)
    cf, _ = fd.get_cash_flow_annual(ticker)

    ratios = compute_ratios_from_av(bs, is_, cf, sector)
    df_input = pd.DataFrame([ratios])

    X_proc = preprocessor.transform(df_input)

    # grouped prediction (High/Medium/Low)
    pred_enc = rf_model.predict(X_proc)
    pred_label = le.inverse_transform(pred_enc)[0]

    # probability of the predicted group
    group_idx = le.transform([pred_label])[0]
    group_proba = float(rf_model.predict_proba(X_proc)[0][group_idx])

    # expand into original ratings
    orig_dist = group_to_original[pred_label]
    expanded_probs = {rating: float(p) * group_proba for rating, p in orig_dist.items()}
    final_rating = max(expanded_probs, key=expanded_probs.get)

    # explanation: top 3 features
    importances = rf_model.feature_importances_
    feature_names = preprocessor.get_feature_names_out()
    top_idx = np.argsort(importances)[::-1][:3]
    explanation = ", ".join(feature_names[i] for i in top_idx)

    return {
        "ticker": ticker,
        "sector": sector,
        "group_prediction": pred_label,
        "final_rating": final_rating,
        "ratios": ratios,
        "explanation": f"Top drivers: {explanation}"
    }

# ------------------------------
# Run for a test ticker
# ------------------------------
if __name__ == "__main__":
    result = predict_from_alphavantage("AAPL", "TECHNOLOGY")

    print(f"\n📊 Credit Rating Prediction for {result['ticker']} ({result['sector']})")
    print(f"➡️ Group Prediction: {result['group_prediction']}")
    print(f"➡️ Final Predicted Rating: {result['final_rating']}")
    print(f"📝 Explanation: {result['explanation']}")
