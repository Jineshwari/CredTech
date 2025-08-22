# explainability.py
import pandas as pd

def generate_explanation(score, feature_importances, features, trends=None):
    """
    Feature-level explanations, trends, plain-language summary.
    No LLM used.
    """
    explanation = {
        'score': score,
        'feature_breakdowns': feature_importances,
        'trend_indicators': trends or {'short_term': 'Stable', 'long_term': 'Improving'},  # Use provided trends or mock
        'reasoning': []  # Event-based, but for structured only
    }
    
    # Plain-language summary based on rules
    summary = f"Credit score of {score:.2f} is influenced by: "
    top_features = sorted(feature_importances, key=feature_importances.get, reverse=True)[:3]
    for feat in top_features:
        val = features[feat]  # Directly use the scalar value from the dictionary
        if feat == 'debt_to_equity':
            summary += f"High debt-to-equity ({val:.2f}) increasing risk, " if val > 1 else f"Low debt-to-equity ({val:.2f}) supporting stability, "
        elif feat == 'current_ratio':
            summary += f"Strong current ratio ({val:.2f}) indicating liquidity, " if val > 1.5 else f"Weak current ratio ({val:.2f}) raising concerns, "
        elif feat == 'profit_margin':
            summary += f"Positive profit margin ({val:.2f}) boosting score, " if val > 0 else f"Negative profit margin ({val:.2f}) lowering score, "
    explanation['summary'] = summary.strip(', ')
    
    return explanation