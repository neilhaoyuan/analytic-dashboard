import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from app import cache
import time

"""

VWAP Related Functions

"""

# Calculates VWAP and Z-score from VWAP, using typical price and volume of stock
def get_intraday_vwap(ohlc_df):
    df = ohlc_df.copy()

    # Calculate typical price (used as it more accurately represents price than just close)
    df['Typical Price'] = (df['High'] * df['Low'] * df['Close']) / 3

    # Find specific day, group the cumulative volume based on each day (resets for each cumulaitve)
    df['Date'] = df.index.date
    df['Cumulative Volume'] = df.groupby('Date')['Volume'].cumsum()

    # Calculate VWAP at each price using: Sum of (Typical Price * Volume) / Sum of Volume
    df['TP Volume'] = (df['Typical Price'] * df['Volume'])
    df['Cum TP Volume'] = df.groupby('Date')['TP Volume'].cumsum()
    df['VWAP'] = df['Cum TP Volume'] / df['Cumulative Volume']

    # Calculate standard deviation of price from VWAP and the z-score of each price
    df['Deviation'] = df['Close'] - df['VWAP']
    df['VWAP Std'] = df.grouby('Date')['Deviation'].expanding().std().reset_index(level=0, drop=True)
    df['VWAP Z Score'] = df['Deviation'] / df['VWAP Std']

    return df

# Detects VWAP snapback/reversal events, when Z-score is larger than 1 (more than 1 std) and then comes back and crosses VWAP
def detect_vwap_events(vwap_df):
    df = vwap_df.copy()

    # Detect any time z-score extends beyond 1 std away from VWAP
    extended = df['VWAP Z Score'].abs() > 1

    # Detect any time price crosses VWAP, i.e. above -> below, below -> above
    cross_zero = (df['VWAP Z Score'].shift(1) * df['VWAP Z Score']) < 0

    # Group by zero crossings
    group = cross_zero.cumsum()

    # Within each group check if any close price in that group was extended, return proper boolean
    any_extended = extended.groupby(group).transform('any')

    # Detect snapback events when price crosses zero while also have any extended 
    df['VWAP Event'] = cross_zero & any_extended
    
    return df


"""

Volume Profile 

"""

# Calculates basic volume profile by splitting prices into bins and finding total volume for each bin
def get_volume_profile(ohlc_df, num_bins=50):
    df = ohlc_df.copy()

    # Creates bins
    df['Price Bin'] = pd.cut(df['Close'], bins=num_bins)
    
    # Group and aggregate the data
    profile = df.groupby('Price Bin').agg({
        'Volume': 'sum',
        'Close': 'mean'
    }).reset_index()
        
    # Return properly named df
    return profile.rename({'Volume': 'Total Volume', 'Close': 'Avg Price'}, axis=1).dropna()

# Determines the point of control, value area, and high volume nodes
def get_profile_info(profile_df):
    df = profile_df.copy()
    
    # POC info
    poc_price = df['Avg Price'].loc[df['Total Volume'].idxmax()]

    
