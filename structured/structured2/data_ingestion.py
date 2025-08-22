import yfinance as yf
import pandas as pd
import requests
import os
import time
from dotenv import load_dotenv
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache

load_dotenv()

FRED_API_KEY = os.getenv('FRED_API_KEY')
FRED_BASE_URL = 'https://api.stlouisfed.org/fred/series/observations'

@lru_cache(maxsize=1)
def fetch_fred_data(series_id='FEDFUNDS'):
    """
    Fetch macroeconomic data from FRED for the latest available data.
    Handles retries and validates response.
    """
    today = datetime.now().date()
    start_date = today - timedelta(days=30)  # Extended to 30 days for context
    
    params = {
        'series_id': series_id,
        'api_key': FRED_API_KEY,
        'file_type': 'json',
        'observation_start': start_date.strftime('%Y-%m-%d'),
        'observation_end': today.strftime('%Y-%m-%d')
    }
    for attempt in range(3):
        try:
            response = requests.get(FRED_BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'observations' not in data or not data['observations']:
                print(f"Warning: No observations found for {series_id} within the last 30 days. Using latest available.")
                params_fallback = {
                    'series_id': series_id,
                    'api_key': FRED_API_KEY,
                    'file_type': 'json'
                }
                response_fallback = requests.get(FRED_BASE_URL, params=params_fallback)
                response_fallback.raise_for_status()
                data_fallback = response_fallback.json()
                if 'observations' not in data_fallback or not data_fallback['observations']:
                    print(f"Warning: No data available for {series_id}. Returning None.")
                    return None
                observations = data_fallback['observations']
            else:
                observations = data['observations']
            
            if isinstance(observations[0], dict) and 'date' in observations[0] and 'value' in observations[0]:
                df = pd.DataFrame(observations)[['date', 'value']].sort_values('date', ascending=False)
            else:
                print(f"Warning: Unexpected observation format for {series_id}. Returning None.")
                return None
            
            df['value'] = pd.to_numeric(df['value'], errors='coerce')
            df['date'] = pd.to_datetime(df['date'])
            
            latest_value = df.iloc[0]['value'] if not df.empty else None
            latest_date = df.iloc[0]['date'] if not df.empty else None
            if latest_date:
                print(f"Using FRED data for {series_id} from {latest_date.date()}.")
            return latest_value
        except requests.exceptions.RequestException as e:
            print(f"Error fetching FRED for {series_id}: {e}. Retrying...")
            time.sleep(2 ** attempt)
        except (KeyError, ValueError) as e:
            print(f"Error fetching FRED for {series_id}: Unexpected response format - {e}. Retrying...")
            time.sleep(2 ** attempt)
        except Exception as e:
            print(f"Error fetching FRED for {series_id}: {e}. Retrying...")
            time.sleep(2 ** attempt)
    raise Exception(f"Failed to fetch FRED data for {series_id} after retries.")

def fetch_yfinance_data(ticker):
    """
    Fetch structured data from Yahoo Finance: financial statements and daily stock prices for the last 30 days.
    Handles retries for fault tolerance.
    """
    today = datetime.now().date()
    start_date = today - timedelta(days=30)
    
    for attempt in range(3):
        try:
            stock = yf.Ticker(ticker)
            balance_sheet = stock.balance_sheet.transpose()
            income_stmt = stock.income_stmt.transpose()
            cash_flow = stock.cashflow.transpose()
            
            latest_bs = balance_sheet.iloc[0] if not balance_sheet.empty else pd.Series()
            latest_is = income_stmt.iloc[0] if not income_stmt.empty else pd.Series()
            latest_cf = cash_flow.iloc[0] if not cash_flow.empty else pd.Series()
            
            hist = stock.history(start=start_date, end=today + timedelta(days=1))  # +1 to include today
            close_prices = hist['Close'].to_dict() if not hist.empty else {}
            
            data = {
                'ticker': ticker,
                'total_assets': latest_bs.get('Total Assets', None),
                'total_liabilities': latest_bs.get('Total Liabilities Net Minority Interest', None),
                'total_equity': latest_bs.get('Stockholders Equity', None),
                'revenue': latest_is.get('Total Revenue', None),
                'net_income': latest_is.get('Net Income', None),
                'operating_cash_flow': latest_cf.get('Operating Cash Flow', None),
                'close_prices': close_prices
            }
            return data
        except Exception as e:
            print(f"Error fetching yfinance for {ticker}: {e}. Retrying...")
            time.sleep(2 ** attempt)
    raise Exception(f"Failed to fetch yfinance data for {ticker} after retries.")

def process_data(raw_data, macro_rate):
    """
    Clean, normalize, and extract features.
    Features: debt_to_equity, current_ratio, profit_margin, roa, price_volatility.
    Impute missing with 0 or mean.
    """
    features = {}
    ta = raw_data.get('total_assets', 0)
    tl = raw_data.get('total_liabilities', 0)
    te = raw_data.get('total_equity', 0)
    rev = raw_data.get('revenue', 0)
    ni = raw_data.get('net_income', 0)
    ocf = raw_data.get('operating_cash_flow', 0)
    prices = raw_data.get('close_prices', {})
    
    # Calculate price volatility over 30 days
    price_list = list(prices.values())
    features['price_volatility'] = pd.Series(price_list).pct_change().std() if len(price_list) > 1 else 0
    
    features['debt_to_equity'] = tl / te if te != 0 else 0
    features['current_ratio'] = ta / tl if tl != 0 else 1
    features['profit_margin'] = ni / rev if rev != 0 else 0
    features['roa'] = ni / ta if ta != 0 else 0
    features['macro_interest_rate'] = macro_rate if macro_rate is not None else 0
    
    for k in features:
        if k == 'debt_to_equity':
            features[k] = min(max(features[k], 0), 5) / 5
        elif k == 'current_ratio':
            features[k] = min(max(features[k], 0), 3) / 3
    
    return pd.DataFrame([features])

def ingest_data_for_issuers(issuers, max_workers=5):
    """
    Ingest and process for multiple issuers for the last 30 days. Batched with parallel processing.
    """
    today = datetime.now().date()
    start_date = today - timedelta(days=30)
    print(f"Fetching data for {start_date} to {today}")
    
    macro_rate = fetch_fred_data()
    data = {}
    
    def process_ticker(ticker):
        try:
            raw = fetch_yfinance_data(ticker)
            processed = process_data(raw, macro_rate)
            return ticker, processed
        except Exception as e:
            print(f"Skipping {ticker}: {e}")
            return ticker, None
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_ticker = {executor.submit(process_ticker, ticker): ticker for ticker in issuers}
        for future in as_completed(future_to_ticker):
            ticker = future_to_ticker[future]
            try:
                ticker, result = future.result()
                if result is not None:
                    data[ticker] = result
            except Exception as e:
                print(f"Error processing {ticker}: {e}")
            time.sleep(0.1)
    
    return data