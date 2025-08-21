# unstructured/sentiment.py
import spacy
from spacy.matcher import PhraseMatcher

nlp = spacy.load("en_core_web_sm")
CREDIT_KEYWORDS = {"negative": ["debt", "bankruptcy", "default", "downgrade", "decline", "loss", "cyberattack", "fraud", "probe"], "positive": ["funding", "growth", "profit", "upgrade"]}
CREDIT_PHRASES = {"high_risk": ["debt restructuring", "credit downgrade", "financial loss", "legal investigation", "cyberattack breach"], "medium_risk": ["declining sales", "market share loss", "data breach", "regulatory probe", "stock sale", "insider selling", "breach reported", "sold", "breach", "breaches"], "positive_event": ["successful funding", "profit growth"]}

def analyze_sentiment(text, score):
    doc = nlp(text)
    sentiment_label = "positive" if score > 0 else "negative" if score < 0 else "neutral"
    return sentiment_label

def detect_risk(text, sentiment):
    risk_factor = "low"
    doc = nlp(text)
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    for category, phrases in CREDIT_PHRASES.items():
        patterns = [nlp(phrase.lower()) for phrase in phrases]
        matcher.add(category, patterns)
    matches = matcher(doc)
    for _, _, _ in matches:
        if "high_risk" in [nlp.vocab.strings[match_id] for match_id, _, _ in matches]:
            risk_factor = "high"
            break
        elif "medium_risk" in [nlp.vocab.strings[match_id] for match_id, _, _ in matches]:
            risk_factor = "medium"
    if risk_factor == "low" and sentiment < -0.01:
        risk_factor = "medium"
    return risk_factor