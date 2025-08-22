import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib
import json
import os

# ------------------------
# Load dataset
# ------------------------
df = pd.read_csv("structured/corporateCreditRatingWithFinancialRatios.csv")

# ✅ Only keep the features you want
feature_cols = [
    'Sector', 'Current Ratio', 'Long-term Debt / Capital', 'Debt/Equity Ratio',
    'Gross Margin', 'Operating Margin', 'EBIT Margin', 'Pre-Tax Profit Margin',
    'Net Profit Margin', 'Asset Turnover', 'ROE - Return On Equity',
    'ROA - Return On Assets', 'Operating Cash Flow Per Share', 'Free Cash Flow Per Share'
]

X = df[feature_cols].copy()
y_original = df['Rating'].copy()   # fine-grained labels (AAA…D)

# ------------------------
# Collapse ratings into groups
# ------------------------
def collapse_rating(r):
    if r in ['AAA', 'AA+', 'AA', 'AA-', 'A+', 'A', 'A-']:
        return 'High'
    elif r in ['BBB+', 'BBB', 'BBB-']:
        return 'Medium'
    else:
        return 'Low'

y_grouped = y_original.apply(collapse_rating)

# ------------------------
# Train-test split
# ------------------------
# Split stratified by grouped labels (not fine-grained)
X_train, X_test, y_train_orig, y_test_orig = train_test_split(
    X, y_original, test_size=0.2, stratify=y_grouped, random_state=42
)


y_train = y_train_orig.apply(collapse_rating)   # grouped (High/Medium/Low)
y_test  = y_test_orig.apply(collapse_rating)

# ------------------------
# Build distribution: P(original | group)
# ------------------------
dist_df = (
    pd.DataFrame({"group": y_train, "rating": y_train_orig})
      .groupby(["group", "rating"])
      .size()
      .groupby(level=0)
      .apply(lambda s: (s / s.sum()).round(6))  # normalize
      .unstack(fill_value=0)
)

group_to_original_dist = dist_df.to_dict(orient="index")

# Save JSON for predict.py
os.makedirs("structured", exist_ok=True)
# Convert tuple keys to strings for JSON
# ------------------------
# Save group → original distribution mapping
# ------------------------
import json

group_to_original_dist_str = {}

for group, dist in group_to_original_dist.items():
    # group yahan tuple aa raha hai jaise ('Low','Low'), hum sirf ek value lenge
    if isinstance(group, tuple):
        group_str = group[0]
    else:
        group_str = str(group)

    dist_str = {str(r): float(p) for r, p in dist.items()}
    group_to_original_dist_str[group_str] = dist_str

with open("structured/group_label_distribution.json", "w") as f:
    json.dump(group_to_original_dist_str, f, indent=2)

print("✅ Saved probabilistic mapping to structured/group_label_distribution.json")


# ------------------------
# Encode grouped target labels
# ------------------------
le = LabelEncoder()
y_train_enc = le.fit_transform(y_train)
y_test_enc = le.transform(y_test)

# ------------------------
# Preprocessing (OHE for Sector)
# ------------------------
preprocessor = ColumnTransformer(
    transformers=[
        ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), ['Sector']),
        ('num', 'passthrough', [col for col in feature_cols if col != 'Sector'])
    ]
)

X_train_proc = preprocessor.fit_transform(X_train)
X_test_proc = preprocessor.transform(X_test)

# ------------------------
# Train model
# ------------------------
rf = RandomForestClassifier(
    n_estimators=200, random_state=42, class_weight='balanced'
)
rf.fit(X_train_proc, y_train_enc)

# ------------------------
# Evaluate
# ------------------------
y_pred = rf.predict(X_test_proc)
print("Accuracy:", accuracy_score(y_test_enc, y_pred))
print("\nClassification Report:\n", classification_report(y_test_enc, y_pred, target_names=le.classes_))

# ------------------------
# Save artifacts
# ------------------------
joblib.dump(rf, "structured/credit_rf_model.joblib")
joblib.dump(preprocessor, "structured/preprocessor.joblib")
joblib.dump(le, "structured/label_encoder.joblib")

print("✅ Model, Preprocessor, Label Encoder, and Mapping saved.")
