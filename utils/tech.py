import numpy as np
import pandas as pd
from utils.config import annualization_factors

"""
VWAP Related Functions
"""

# Calculates VWAP and Z-score from VWAP, using typical price and volume of stock
def get_intraday_vwap(ohlc_df):
    df = ohlc_df.copy()

    # Calculate typical price (used as it more accurately represents price than just close)
    df['Typical Price'] = (df['High'] + df['Low'] + df['Close']) / 3

    # Remove any existing 'Date' column and clear index name
    if 'Date' in df.columns:
        df = df.drop('Date', axis=1)
    
    # Clear the index name completely to avoid ambiguity
    df.index.name = None

    # Find specific day, group the cumulative volume based on each day (resets for each cumulaitve)
    df['Date'] = pd.to_datetime(df.index).date
    df['Cumulative Volume'] = df.groupby('Date')['Volume'].cumsum()

    # Calculate VWAP at each price using: Sum of (Typical Price * Volume) / Sum of Volume
    df['TP Volume'] = (df['Typical Price'] * df['Volume'])
    df['Cum TP Volume'] = df.groupby('Date')['TP Volume'].cumsum()
    df['VWAP'] = df['Cum TP Volume'] / df['Cumulative Volume']

    # Calculate standard deviation of price from VWAP and the z-score of each price
    df['Deviation'] = df['Close'] - df['VWAP']
    df['VWAP Std'] = df.groupby('Date')['Deviation'].expanding().std().reset_index(level=0, drop=True)
    df['VWAP Std'] = df['VWAP Std'].fillna(method='bfill')
    df['VWAP Z Score'] = df['Deviation'] / df['VWAP Std']

    return df

# Detects VWAP snapback/reversal events, when Z-score is larger than 1 (more than 1 std) and then comes back and crosses VWAP
def detect_vwap_events(vwap_df):
    df = vwap_df.copy()

    # Detect any time z-score extends beyond 2 std away from VWAP, then detect any crossings
    extended = df['VWAP Z Score'].abs() > 2
    cross_zero = (df['VWAP Z Score'].shift(1) * df['VWAP Z Score']) < 0

    # Only consider crossings on the same day
    same_day = df['Date'] == df['Date'].shift(1)
    valid_cross = cross_zero & same_day

    df['VWAP Event'] = False
    has_extended = False
    current_date = None

    # Loop through each day to detect snapback events: must have has_extended be true and a valid cross
    for i in df.index:

        # Reset has_extended on a new day
        if df['Date'].loc[i] != current_date:
            has_extended = False
            current_date = df['Date'].loc[i]

        # Check if extended
        if extended.loc[i]:
            has_extended = True
        
        # Check if its a valid crossing, if so mark that VWAP event down and reset has_extended
        if valid_cross.loc[i] and has_extended:
            df['VWAP Event'].loc[i] = True
            has_extended = False

    # Track maximum and minimum z score seen so far and then find the maximum extension/distance
    cummax = df.groupby('Date', observed=True)['VWAP Z Score'].cummax()
    cummin = df.groupby('Date', observed=True)['VWAP Z Score'].cummin()
    largest = cummax.abs() >= cummin.abs()
    max_extension = np.where(largest, cummax, cummin)

    # Keep onkly the max extension distance 
    df['Max Z Distance'] = np.where(df['VWAP Event'], max_extension, None)
    
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
        
    return profile.rename({'Volume': 'Total Volume', 'Close': 'Avg Price'}, axis=1).dropna()

# Determines the point of control, value area, and high volume nodes
def get_profile_info(profile_df):
    df = profile_df.copy().sort_values('Avg Price').reset_index(drop=True)

    # Determing POC info
    poc_idx = df['Total Volume'].idxmax()
    poc_price = df['Avg Price'].iloc[poc_idx]
    
    # Variables needed for value area algorithm
    target_volume = df['Total Volume'].sum() * 0.7
    cumulative_volume = df['Total Volume'].iloc[poc_idx]
    above_idx = poc_idx + 1
    below_idx = poc_idx - 1

    # Algorithm to find value area, aka the smallest continuous price range that contains 70% of the volume
    while cumulative_volume < target_volume:
        # Determine volume above and below
        above_vol = df['Total Volume'].iloc[above_idx] if above_idx < len(df) else 0
        below_vol = df['Total Volume'].iloc[below_idx] if below_idx >= 0 else 0

        # Expand cumulative towards the larger volume
        if above_vol >= below_vol and above_idx < len(df):
            cumulative_volume += above_vol
            above_idx += 1
        elif below_idx >= 0:
            cumulative_volume += below_vol
            below_idx -= 1
        else:
            break 

    # Value area price bounds 
    value_area_high = df['Avg Price'].iloc[above_idx - 1]
    value_area_low = df['Avg Price'].iloc[below_idx + 1]

    high_volume_nodes = df.nlargest(5, 'Total Volume')['Avg Price'].tolist()

    return {'POC': poc_price, 
            'Value Area High': value_area_high,
            'Value Area Low': value_area_low,
            'High Volume Nodes': high_volume_nodes}

"""
Rolling Realized Volatility
"""

# Determines rolling realized volatility of close prices
def get_realized_volatility(ohlc_df, interval):
    df = ohlc_df.copy()

    # Calculates rolling window, minimum 10, maximum of 10% of total data length, and then returns and rolling std
    window = max(10, int(len(df) * 0.1))
    df['% Returns'] = df['Close'].pct_change()
    rolling_std = df['% Returns'].rolling(window).std()

    # Annualize rolling volatility
    factor = annualization_factors.get(interval)
    df['Annualized Volatility'] = rolling_std * factor

    return df.dropna()

"""
Rolling Beta
"""

# Determines the rolling beta in relation to SMP 500 benchmark 
def get_rolling_beta(ohlc_df, benchmark_df):
    # Set up combined dataframe
    df = ohlc_df.copy()
    bench_df = benchmark_df.copy()
    combined = pd.merge(df['Close'], bench_df['Close'], left_index=True, right_index=True, how='inner', suffixes=('', '_benchmark'))

    # Calculate returns and rolling window based on length of data 
    combined['Stock Returns'] = combined['Close'].pct_change()
    combined['Benchmark Returns'] = combined['Close_benchmark'].pct_change()
    window = max(10, int(len(combined) * 0.1))

    # Calculating rolling beta, beta = cov(stock and market) / var 
    rolling_beta = (combined['Stock Returns'].rolling(window).cov(combined['Benchmark Returns']) / 
                    combined['Benchmark Returns'].rolling(window).var())
    
    return rolling_beta.dropna()