import unittest
from data_ingestion import fetch_yfinance_data, fetch_fred_data, process_data
from scoring_engine import ScoringEngine
import pandas as pd  # Added import for pandas

class TestIngestion(unittest.TestCase):
    def test_yfinance(self):
        data = fetch_yfinance_data('AAPL')
        self.assertIn('total_assets', data)

    def test_fred(self):
        rate = fetch_fred_data()
        self.assertIsNotNone(rate)

    def test_process(self):
        raw = {'total_assets': 1000, 'total_liabilities': 500, 'total_equity': 500, 'revenue': 200, 'net_income': 50, 'operating_cash_flow': 100, 'close_prices': [100, 105, 102]}
        processed = process_data(raw, 0.05)
        self.assertEqual(processed['debt_to_equity'][0], 0.2)  # Updated to expect normalized value (1.0 / 5 = 0.2)

class TestScoring(unittest.TestCase):
    def test_predict(self):
        engine = ScoringEngine()
        X = pd.DataFrame({'debt_to_equity': [0.5], 'current_ratio': [2.0], 'profit_margin': [0.1], 'roa': [0.05], 'price_volatility': [0.02], 'macro_interest_rate': [0.05]})
        score = engine.predict(X)
        self.assertGreater(score, 0)

if __name__ == '__main__':
    unittest.main()