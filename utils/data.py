import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from utils.config import period_map, interval_map, valid_intervals_map
import requests

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
})

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
        return pd.DataFrame()

    closes = {} # Dictionary holding close prices

    # Loops through list and adds close prices
    for t in ticker_list:
        df = get_ohlc_data(t, period, interval)
        if not df.empty:
            closes[t] = df["Close"]

    if not closes:
        return pd.DataFrame()
    
    df = pd.DataFrame(closes).dropna()

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
        sector = yf.Ticker(ticker).info.get('sector')
        sector = "N/A" if sector is None else sector
        sector_data.append({
                    'Ticker': ticker,
                    'Sector': sector})
    
    df = pd.DataFrame(sector_data)
    
    return df

# Get summary table
def get_summary_table(ticker_list, shares_dict, period, interval, port_page):
    if (not ticker_list or not shares_dict) and port_page:
        return pd.DataFrame()
    
    summary_table = []
    total_value = 0

    for ticker in ticker_list:
        ohlc_data = get_ohlc_data(ticker, period, interval)
        
        volume = ohlc_data['Volume'].iloc[-1]
        initial_price = ohlc_data.dropna()['Close'].iloc[0]
        current_price = ohlc_data.dropna()['Close'].iloc[-1]
        return_pct = ((current_price - initial_price) / initial_price) * 100
        intervally_returns = ohlc_data['Close'].pct_change().dropna()

        average_intervally_returns = intervally_returns.mean() * 100
        std_dev = intervally_returns.std() * 100
        sharpe_ratio = average_intervally_returns / std_dev

        cum_return = (1 + intervally_returns).cumprod()
        cum_max = cum_return.cummax()
        drawdown = (cum_return - cum_max) / cum_max * 100
        max_drawdown = drawdown.min()

        if port_page:
            num_shares = shares_dict.get(ticker)
            value = current_price * num_shares
            total_value += value

            sector = yf.Ticker(ticker).info.get('sector')
            sector = "N/A" if sector is None else sector

            summary_table.append({
                'Ticker': ticker,
                '% Return': return_pct,
                'Average % Return': average_intervally_returns,
                '% Returns Std Dev': std_dev,
                'Max Drawdown %': max_drawdown,
                'Sharpe Ratio': sharpe_ratio,
                'Current Volume': volume, 
                'Current Price ($)': current_price,
                'Sector': sector,
                'Shares': num_shares,
                'Portfolio Value': value
            })

            if not summary_table:
                return pd.DataFrame()

            df = pd.DataFrame(summary_table)
            df['Current Price ($)'] = df['Current Price ($)'].round(2)
            df['Portfolio Value'] = df['Portfolio Value'].round(2)
            df['% Return'] = df['% Return'].round(2)
            df['% Returns Std Dev'] = df['% Returns Std Dev'].round(2)
            df['% Portfolio Value'] = ((df['Portfolio Value'] / total_value) * 100).round(2)
            df['Average % Return'] = df['Average % Return'].round(2)
            df['Sharpe Ratio'] = df['Sharpe Ratio'].round(2)
            df['Max Drawdown %'] = df['Max Drawdown %'].round(2)

        else:
            summary_table.append({
                'Ticker': ticker,
                '% Return': return_pct,
                'Average % Return': average_intervally_returns,
                '% Returns Std Dev': std_dev,
                'Max Drawdown %': max_drawdown,
                'Sharpe Ratio': sharpe_ratio,
                'Current Price ($)': current_price,
            })

            df = pd.DataFrame(summary_table)
            df['Current Price ($)'] = df['Current Price ($)'].round(2)
            df['% Return'] = df['% Return'].round(2)
            df['% Returns Std Dev'] = df['% Returns Std Dev'].round(2)
            df['Average % Return'] = df['Average % Return'].round(2)
            df['Sharpe Ratio'] = df['Sharpe Ratio'].round(2)
            df['Max Drawdown %'] = df['Max Drawdown %'].round(2)

    return df

def create_candlestick_graph(ohlc_df, title):
    # Empty ticker, no figure generated
    if ohlc_df.empty:
        return go.Figure()

    initial_price = ohlc_df.dropna()["Close"].iloc[0]
    current_price = ohlc_df.dropna()["Close"].iloc[-1]
    pct_change = ((current_price - initial_price) / initial_price) * 100
    
    color = 'green' if pct_change >= 0 else 'red'
    sign = '+' if pct_change >= 0 else ''
    pct_label = f"{title} <span style='color:{color}'>{sign}{pct_change:.2f}%</span>"

    fig = go.Figure(go.Candlestick(
        x=ohlc_df.index,
        open=ohlc_df["Open"],
        high=ohlc_df["High"],
        low=ohlc_df["Low"],
        close=ohlc_df["Close"],
    )).update_layout(title=pct_label, 
                     paper_bgcolor='rgba(0, 0, 0, 0)', 
                     plot_bgcolor='#1e1e1e', 
                     font={'color': 'white'},
                     xaxis_rangeslider_visible=False)
    
    return fig

def get_news(ticker_list, article_amnt):
    if not ticker_list:
        return pd.DataFrame()
    
    news_list = []

    for ticker in ticker_list:
        try:
            stock = yf.Ticker(ticker)
            news = stock.news[:article_amnt]

            for article in news:
                content = article['content']
                
                news_list.append({
                    'title': content['title'],
                    'link': content['canonicalUrl']['url'],
                    'image': content['thumbnail']['originalUrl']
                })
        except:
            continue

    news_df = pd.DataFrame(news_list)
    news_df = news_df.drop_duplicates(subset=['title'], keep='first')
    
    return news_df