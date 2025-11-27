import yfinance as yf
import pandas as pd
import numpy as np
import numpy_financial as npf

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

def get_stock_data(ticker, period, interval):
    data_period = period_map.get(period)
    data_interval = interval_map.get(interval)
    ticker = yf.Ticker(ticker)
    data = ticker.history(period=data_period, interval=data_interval)
    return data["Close"]

