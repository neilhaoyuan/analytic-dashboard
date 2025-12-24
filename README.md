# Analytic Dashboard

A Data Visualization project with Dash. 

## Description

A real-time stock market analytics dashboard built with Dash, Plotly, yFinance, and Pandas. Features portfolio tracking, broad market indices analysis, and sector performance visualization. Allows for dynamic user selection of trading period and intervals, and displays quick and readable summary metrics and related news stories.

### Portfolio & Stock Analysis
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

## Configuration
**Time Periods**
Available periods: 1 Day, 5 Days, 1 Month, 3 Months, 6 Months, Year To Date, 1 Year, 2 Years, 5 Years, 10 Years

**Intervals**
Available intervals vary by period:
- Intraday: 5 Minutes, 15 Minutes, 30 Minutes, 1 Hour, 1.5 Hours
- Daily and longer: 1 Day, 5 Days, 1 Week, 1 Month, 3 Months

**Data Sources**
This dashboard uses yfinance to fetch real-time stock market data from Yahoo Finance, due to that it can not be deployed. 

The list of available trackable tickers in the Portfolio dropdown menu come from scraping the NASDAQ and TSX. Check out stocks.py for more details. 



