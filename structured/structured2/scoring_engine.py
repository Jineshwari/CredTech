# scoring_engine.py
from sklearn.tree import DecisionTreeRegressor
import pandas as pd
import numpy as np

class ScoringEngine:
    def __init__(self):
        # Mock historical data for training (in real: load from CSV or DB)
        # Features: debt_to_equity, current_ratio, profit_margin, roa, price_volatility, macro_interest_rate
        self.X_train = pd.DataFrame({
            'debt_to_equity': [0.5, 1.0, 2.0, 0.2, 1.5],
            'current_ratio': [2.0, 1.5, 1.0, 2.5, 1.2],
            'profit_margin': [0.1, 0.05, -0.1, 0.15, 0.08],
            'roa': [0.05, 0.03, -0.02, 0.07, 0.04],
            'price_volatility': [0.02, 0.03, 0.05, 0.01, 0.04],
            'macro_interest_rate': [0.05, 0.04, 0.06, 0.03, 0.05]
        })
        self.y_train = np.array([80, 70, 50, 90, 65])  # Mock scores
        
        self.model = DecisionTreeRegressor(max_depth=3)  # Interpretable
        self.feature_names = self.X_train.columns.tolist()  # Store feature names
        self.retrain()  # Initial train
    
    def retrain(self, new_X=None, new_y=None):
        """
        Incremental retraining: Append new data if provided, retrain.
        """
        if new_X is not None and new_y is not None:
            # Ensure new_X has the same columns and order
            if isinstance(new_X, pd.DataFrame):
                new_X = new_X[self.feature_names]
            elif isinstance(new_X, pd.Series):
                new_X = pd.DataFrame([new_X], columns=self.feature_names)
            else:
                raise ValueError("new_X must be a pandas DataFrame or Series")
            
            self.X_train = pd.concat([self.X_train, new_X], ignore_index=True)
            self.y_train = np.append(self.y_train, new_y)
        self.model.fit(self.X_train, self.y_train)
    
    def predict(self, X):
        """
        Predict credit score (0-100).
        """
        if isinstance(X, pd.DataFrame):
            X = X[self.feature_names]
        elif isinstance(X, pd.Series):
            X = pd.DataFrame([X], columns=self.feature_names)
        else:
            raise ValueError("X must be a pandas DataFrame or Series")
        return self.model.predict(X)[0]
    
    def get_feature_importances(self, X):
        """
        Get feature contributions.
        """
        # For DT, use feature_importances_
        importances = self.model.feature_importances_
        feature_names = self.feature_names
        return dict(zip(feature_names, importances))