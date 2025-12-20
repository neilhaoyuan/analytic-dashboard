import pandas as pd

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

ticker_df = pd.read_csv("total_tickers.csv")
