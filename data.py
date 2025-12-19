import yfinance as yf
import pandas as pd
import numpy as np 
import numpy_financial as npf
from config import period_map, interval_map, valid_intervals_map

def get_valid_interval(period):
    return valid_intervals_map[period]

# Gets Open, High, Low, Close and Volume data
def get_ohlc_data(ticker, period, interval):
    df = yf.Ticker(ticker).history(
        period=period_map[period],
        interval=interval_map[interval]
    )
    return df

def get_close_data(ticker_list, period, interval):
    if not ticker_list:
        return pd.DataFrame(), {}

    closes = {} # Dictionary holding close prices

    # Loops through list and adds close prices
    for t in ticker_list:
        df = get_ohlc_data(t, period, interval)
        if not df.empty:
            closes[t] = df["Close"]

    if not closes:
        return pd.DataFrame(), {}
    
    df = pd.DataFrame(closes).dropna()
    pct_change = ((df.iloc[-1] / df.iloc[0] - 1) * 100).to_dict()

    return df, pct_change

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

# Get cumulative returns
def get_cumulative_returns(closes_df, shares_dict):
    if closes_df.empty or not shares_dict:
        return pd.DataFrame()
    
    # Convert to series to allow for dataframe + series manipulation
    shares_series = pd.Series(shares_dict)

    portfolio_value = (closes_df * shares_series).sum(axis=1)
    cumulative_return_pct = (portfolio_value / portfolio_value.iloc[0] - 1) * 100

    return pd.DataFrame({
        'Portfolio Value': portfolio_value,
        'Cumulative Return (%)': cumulative_return_pct})

# Get volume data
def get_volume_data(ticker, period, interval):
    if ticker == None:
        return pd.DataFrame
    
    volume = get_ohlc_data(ticker, period, interval)["Volume"]
    
    return volume.dropna()

# Get sector information
def get_sector_info(ticker_list):
    if not ticker_list:
        return pd.DataFrame()
    
    sector_data = []
    
    for ticker in ticker_list:
        try:
            sector = yf.Ticker(ticker).info.get('sector')
            sector_data.append({
                    'Ticker': ticker,
                    'Sector': sector})
        except:
            sector_data.append({
                    'Ticker': ticker,
                    'Sector': 'N/A'})
    
    df = pd.DataFrame(sector_data)
    
    return df