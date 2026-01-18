# Analytic Dashboard

A Data Visualization project with Dash and Flask.

<img width="959" height="485" alt="image" src="https://github.com/user-attachments/assets/442cda49-d587-4ecd-a108-de6297b4c576" />


## Description

A real-time stock market analytics dashboard built with Dash, Flask, Plotly, yFinance, and Pandas. Features technical analysis (VWAP mean-reversion, volume profile), portfolio tracking, broad market indices analysis, and sector performance visualization. Allows for dynamic user selection of trading period and intervals, and displays quick and readable summary metrics and related news stories.

### Technical Stock Analysis
- Analyze individual stocks for various technical indicators
- Tracks Volume Weighted Average Price (VWAP) and detects VWAP Snapback events: when price extends beyond VWAP by 2 standard deviations and then crosses back to VWAP
- Volume Profile with point of control and resistance/support bands visualization
- Rolling Realized Volatility and Rolling Beta charts 

### Portfolio Analysis
- Track multiple stocks in your personal portfolio
- Real-time portfolio value and performance metrics
- Individual stock performance visualization
- Sector allocation analysis
- Cumulative returns tracking
- Key metrics: % Return, Sharpe Ratio, Max Drawdown, Standard Deviation

### Broad Market Analysis
- Monitor major market indices (S&P 500, NASDAQ, Russell 2000, etc.)
- Track commodity prices (Gold)
- Currency indices (US Dollar, Canadian Dollar)
- Treasury yield curves
- Volatility Index (VIX)
- Interactive candlestick charts with customizable time periods

### Sector Based Analysis
- 11 major sector ETFs tracking
- Sector correlation heatmap visualization 
- Individual sector performance charts
- Comparative sector analysis

### Dynamic User Features
- Multiple time periods: 1 Day to 10 Years
- Flexible intervals: 5 Minutes to 3 Months
- Scrollable data tables with conditional formatting
- Daily updating news pertaining to related stocks/indices/sectors

![Dashboard Demo](assets/dashboard-updated.gif)


## Usage Instructions
1. Clone the repository
````bash
git clone https://github.com/user/repo.git
cd repo
````
2. Install Dependencies
````bash
pip install -r requirements.txt
````
3. Run the application
````bash
python index.py
````
4. Open your browser and navigate to the localhost server
5. Use the dashboard

**Data Sources**  
This dashboard uses yfinance to fetch real-time stock market data from Yahoo Finance. 

The list of available trackable tickers in the Portfolio dropdown menu come from scraping the NASDAQ and TSX. Check out stocks.py for more details. 



