import pandas as pd
import os
import numpy as np

period_map = {
    '10 Years': '10y', '5 Years': '5y', '2 Years': '2y', '1 Year': '1y',
    'Year To Date': 'ytd', '6 Months': '6mo', '3 Months': '3mo',
    '1 Month': '1mo', '5 Days': '5d', '1 Day': '1d'
}

interval_map = {
    '5 Minutes': '5m', '15 Minutes': '15m',
    '30 Minutes': '30m', '1 Hour': '60m', '1.5 Hours': '90m',
    '1 Day': '1d', '5 Days': '5d', '1 Week': '1wk',
    '1 Month': '1mo', '3 Months': '3mo'
}

valid_intervals_map = {
    '10 Years': ['1 Day', '5 Days', '1 Week', '1 Month', '3 Months'],
    '5 Years': ['1 Day', '5 Days', '1 Week', '1 Month', '3 Months'],
    '2 Years': ['1 Day', '5 Days', '1 Week', '1 Month', '3 Months'],
    '1 Year': ['1 Day', '5 Days', '1 Week', '1 Month', '3 Months'],
    'Year To Date': ['1 Day', '5 Days', '1 Week', '1 Month', '3 Months'],
    '6 Months': ['30 Minutes', '1 Hour', '1.5 Hours', '1 Day', '5 Days', '1 Week', '1 Month', '3 Months'],
    '3 Months': ['15 Minutes', '30 Minutes', '1 Hour', '1.5 Hours', '1 Day', '5 Days', '1 Week', '1 Month', '3 Months'],
    '1 Month': ['5 Minutes', '15 Minutes', '30 Minutes', '1 Hour', '1.5 Hours', '1 Day', '5 Days', '1 Week'],
    '5 Days': ['5 Minutes', '15 Minutes', '30 Minutes', '1 Hour', '1.5 Hours', '1 Day', '5 Days'],
    '1 Day': ['5 Minutes', '15 Minutes', '30 Minutes', '1 Hour', '1.5 Hours', '1 Day']
}

sector_map = {
    'XLC': 'Communications (XLC)',
    'XLY': 'Consumer Discretionary (XLY)',
    'XLP': 'Consumer Staple (XLP)',
    'XLE': 'Energy (XLE)',
    'XLF': 'Financial (XLF)',
    'XLV': 'Healthcare (XLV)',
    'XLI': 'Industrial (XLI)',
    'XLB': 'Materials (XLB)',
    'XLRE': 'Real Estate (XLRE)',
    'XLK': 'Technology (XLK)',
    'XLU': 'Utilities (XLU)'
}

market_map = {
    '^GSPC': 'S&P 500',
    '^IXIC': 'NASDAQ',
    '^RUT': 'Russell 2000',
    '^GSPTSE': 'S&P/TSX Composite',
    '^VIX': 'Volatility Index',
    'GC=F': 'Gold Price Index',
    'DX-Y.NYB': 'US Dollar Index',
    '^XDC': 'CA Dollar Index',
    '^FVX': '5 Year US Treasury Yield',
    '^TYX': '30 Year US Treasury Yield'
}

annualization_factors = {
    '5 Minutes': np.sqrt(252 * 78),         # 252 Trading Days * 78 5 Min Intervals/Trading Day
    '15 Minutes': np.sqrt(252 * 26),        # 252 Trading Days * 26 15 Min Intervals/Trading Day
    '30 Minutes': np.sqrt(252 * 13),        # 252 Trading Days * 13 30 Min Intervals/Trading Day
    '1 Hour': np.sqrt(252 * 6.5),           # 252 Trading Days * 6.5 1 Hour Intervals/Trading Day
    '1.5 Hours': np.sqrt(252 * (13/3)),     # 252 Trading Days * 4.33... 1.5 Hour Intervals/Trading Day
    '1 Day': np.sqrt(252),                  # 252 Trading Days/Year
    '5 Days': np.sqrt(52),                  # For simplicity sake: Aprox 52 Weeks/Year as 5 days aprox 1 trading week
    '1 Week': np.sqrt(52),                  # 52 Weeks/Year
    '1 Month': np.sqrt(12),                 # 12 months/year
    '3 Months': np.sqrt(4)                  # 4 quarters/year
}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ticker_df = pd.read_csv(os.path.join(BASE_DIR, "total_tickers.csv"))
