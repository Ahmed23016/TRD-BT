import requests
from bs4 import BeautifulSoup
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

budget=1000
def get_premarket_stocks():
    global budget
    url="https://www.tradingview.com/markets/stocks-usa/market-movers-pre-market-gainers/"
    try:
        response = requests.get(url)
        response.raise_for_status()  
    except requests.exceptions.RequestException as e:
        print(f"Erllol: {e}")
        return
    soup=BeautifulSoup(response.content, "html.parser")
    rows=scrape_rows(soup)
    tickers=[]
    for i in rows:
        ticker=scrape_ticker(i)
        tickers.append(ticker.text)
    ticker_len=len(ticker)
    up=0
    before_budget=budget
    for i in tickers:
        if calc_perc_diff(i)==2:
            up+=1
    perc= (up/len(tickers)) *100
    print(f"PERCENTAGE {perc}")
    print(f"BEFORE: {before_budget} AFTER: {budget}")
    print(f"BALANCE INCREASE %: {abs(budget - before_budget) / before_budget * 100}")
def scrape_rows(soup):
    target_classes = {"row-RdUXZpkv", "listRow"}
    return soup.find_all("tr", class_=lambda c: c and target_classes == set(c.split()))
def scrape_ticker(soup):
    target_classes={"apply-common-tooltip","tickerNameBox-GrtoTeat","tickerName-GrtoTeat"}
    return soup.find("a",class_=lambda c: c and target_classes == set(c.split()))

def get_data(symbol):
    data = yf.download(symbol, period="max", interval="1m")
    return data
def get_yesterday_close(df,ticker):
    yesterday = datetime.now() - timedelta(1)
    datetime.strftime(yesterday, '%Y-%m-%d')
    yesterday=pd.Timestamp(yesterday)
    yesterday_data=df[df.index.date == yesterday.date()]
    return get_colums(yesterday_data,"Close",ticker,-1)
def get_colums(df,column,ticker,index):
    try:
        return df[(column,ticker)].iloc[index]
    except IndexError:
        print(f"IndexError: Unable to get data at offset {index} for {ticker}.")
        return None

def calc_perc_diff(ticker):
    global budget
    previous_budget = budget
    
    try:
        df = get_data(ticker)
        if df is None or df.empty:
            print(f"No data available for {ticker}.")
            return False

        df.index = pd.to_datetime(df.index)
        print("\n--------------\n")
        print(f"Ticker: {ticker}")

        df = df.reset_index()
        df['Datetime'] = pd.to_datetime(df['Datetime'])
        df.set_index('Datetime', inplace=True)
        
        today = datetime.now().date()

        if today.weekday() == 5:
            today = today - timedelta(days=1)
        elif today.weekday() == 6:
            today = today - timedelta(days=2)

        today = pd.Timestamp(today)

        today_data = df[df.index.date == today.date()]
        if today_data.empty:
            print(f"No data available for today ({today.date()}) for {ticker}.")
            return False

        try:
            first_open = get_colums(today_data, "Open", ticker, 0)
            after_15_open = get_colums(today_data, "Open", ticker, 15)
        except Exception as e:
            print(f"Error retrieving open prices: {e}")
            return False

        if first_open is None or after_15_open is None:
            print(f"Missing open price data for {ticker}.")
            return False

        percentage_difference = abs(after_15_open - first_open) / first_open * 100
        if percentage_difference <= 0:
            print(f"Percentage change is too small to consider a trend.")
            return False

        stok = budget / first_open
        
        potential_new_budget = budget + (after_15_open - first_open) * stok - 5

        if potential_new_budget < budget:
            print(f"Trade not beneficial. .")
        
        budget = potential_new_budget
        
        print(f"FIRST OPEN: {first_open}   AFTER 15 OPEN: {after_15_open}")
        print(f"Percentage Difference: {percentage_difference:.2f}%")
        print(f"Updated Budget: {budget}")
        print("\n--------------\n")

        if percentage_difference > 0:
            return 2  
        else:
            return 1  

    except Exception as e:
        print(f"An error occurred: {e}. Restoring previous budget.")
        budget = previous_budget 
        return False  


    
    

get_premarket_stocks()


