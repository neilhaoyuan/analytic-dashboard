import pandas as pd
import requests
import io

def scrape_us_tickers():
    nasdaq_url = "https://www.nasdaqtrader.com/dynamic/symdir/nasdaqlisted.txt"
    other_url  = "https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt"

    exchange_name_map = {
        "N": "NYSE",
        "A": "AMEX",
        "P": "NYSE ARCA",
        "Z": "BATS",
        "Q": "NASDAQ"}

    # NASDAQ Scraping
    nasdaq_df = pd.read_csv(nasdaq_url, sep='|')
    nasdaq_df = nasdaq_df[['Symbol', 'Security Name', 'Test Issue']]
    nasdaq_df['Exchange'] = "NASDAQ"

    # NYSE and AMEX Scraping
    other_df = pd.read_csv(other_url, sep='|')
    other_df = other_df[['ACT Symbol', 'Security Name', 'Exchange']]
    other_df = other_df.rename(columns={'ACT Symbol': 'Symbol'})

    other_df['Exchange'] = other_df['Exchange'].map(exchange_name_map)

    # Cleaning out test tickers and classed tickers
    nasdaq_df['Symbol'] = nasdaq_df['Symbol'].fillna("")
    nasdaq_df = nasdaq_df[nasdaq_df['Symbol'].str.isalpha()] 
    nasdaq_df = nasdaq_df[nasdaq_df['Test Issue'] == 'N']

    other_df['Symbol'] = other_df['Symbol'].fillna("")
    other_df = other_df[other_df['Symbol'].str.isalpha()]
    other_df = other_df[~other_df['Security Name'].str.contains('test', case=False, na=False)]

    # Combine exchanges
    us_df = pd.concat([nasdaq_df, other_df], ignore_index=True) 
    us_df['Country'] = "US" 
    return us_df

def scrape_canada_tickers():
    tsx_url = "https://www.tsx.com/json/company-directory/search/tsx/%5E*"
    tsxv_url = "https://www.tsx.com/json/company-directory/search/tsxv/%5E*"
    headers = {"User-Agent": "Mozilla/5.0"}

    # TSX Scraping
    tsx_data = requests.get(tsx_url, headers=headers).json()
    tsx_df = pd.json_normalize(tsx_data["results"])

    # TSXV Scraping
    tsxv_data = requests.get(tsxv_url, headers=headers).json()
    tsxv_df = pd.json_normalize(tsxv_data["results"])

    # Only keep symbols
    tsx_df['Symbol'] = tsx_df['symbol'] + '.TO'
    tsxv_df['Symbol'] = tsxv_df['symbol'] + '.V'

    # Adding exchange info
    tsx_df["Exchange"] = 'TSX'
    tsxv_df["Exchange"] = 'TSXV'

    # Renaming
    tsx_df = tsx_df[["Symbol", "name", "Exchange"]].rename(columns={"name": "Security Name"})
    tsxv_df = tsxv_df[["Symbol", "name", "Exchange"]].rename(columns={"name": "Security Name"})
    
    # Combining them 
    ca_df = pd.concat([tsx_df, tsxv_df], ignore_index=True) 
    ca_df["Country"] = "CA"
    return ca_df

def scrape_tickers():
    usa = scrape_us_tickers()
    canada = scrape_canada_tickers()
    total_tickers =  pd.concat([usa, canada], ignore_index=True)
    total_tickers.to_csv("total_tickers.csv", index=False)

    return total_tickers

print(scrape_tickers().head())