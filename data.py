import yfinance as yf
import pandas as pd
import numpy as np 
import numpy_financial as npf
from config import period_map, interval_map, valid_intervals_map

def get_valid_interval(period):
    return valid_intervals_map[period]

def get_close_data(ticker_list, period, interval):
    if not ticker_list:
        return pd.DataFrame(), {}

    closes = {} # Dictionary holding close prices

    # Loops through list and adds close prices
    for t in ticker_list:
        df = yf.Ticker(t).history(
            period=period_map[period],
            interval=interval_map[interval]
        )
        if df.empty:
            continue
        closes[t] = df["Close"]

    if not closes:
        return pd.DataFrame(), {}
    df = pd.DataFrame(closes)

    df = df.dropna()
    pct_change = ((df.iloc[-1] / df.iloc[0] - 1) * 100).to_dict()

    return df, pct_change

# Gets data for candlestick
def get_ohlc_data(ticker, period, interval):
    df = yf.Ticker(ticker).history(
        period=period_map[period],
        interval=interval_map[interval]
    )
    return df

# Used for std, cor, etc
def get_weekly_close(close_df):
    close_df2 = close_df.copy()
    close_df2["Week"] = close_df2.index.to_period("W")
    mask = close_df2["Week"] != close_df2["Week"].shift(-1)
    weekly_close = close_df2.loc[mask].drop(columns="Week")

    return weekly_close

# Correlation matrix
def get_correlation_data(weekly_close):
    weekly_pct = weekly_close.pct_change().dropna()
    corr_matrix = weekly_pct.corr()
    return corr_matrix

