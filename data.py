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

def get_close_data(ticker_list, period, interval):
    if ticker_list is None:
        return pd.DataFrame(), {} 
    
    if isinstance(ticker_list, str):
        ticker_list = [ticker_list]

    all_dfs = []

    for t in ticker_list:
        df = yf.Ticker(t).history(period=period_map[period], interval=interval_map[interval])

        if df.empty:
            continue  # skip broken tickers

        df["Ticker"] = t
        all_dfs.append(df)

    # Combine vertically
    full_df = pd.concat(all_dfs)

    # Percent change per ticker
    pct_change = (
        full_df.groupby("Ticker")["Close"]
               .apply(lambda s: (s.iloc[-1] - s.iloc[0]) / s.iloc[0] * 100)
               .to_dict()
    )

    return full_df, pct_change