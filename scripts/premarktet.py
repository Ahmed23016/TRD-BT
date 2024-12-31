import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

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
    return df[(column,ticker)].iloc[index]
def main():
    ticker="APM"
    df=get_data(ticker)
    df.index = pd.to_datetime(df.index)

    dates = df.index

    df = df.reset_index()

    df['Datetime'] = pd.to_datetime(df['Datetime'])
    df.set_index('Datetime', inplace=True)
    today = datetime.now().date()
    
    if today.weekday() == 5:
        today = today - timedelta(days=1)
    elif today.weekday() == 6:
        today = today - timedelta(days=2)
    yesterday_close=get_yesterday_close(df,ticker)
    print(yesterday_close)
    today = pd.Timestamp(today)
    
    today_data = df[df.index.date == today.date()]
    first_open=get_colums(today_data,"Open",ticker,0)
    after_15_open=get_colums(today_data,"Open",ticker,15)
    percentage_difference = abs(after_15_open - first_open) / first_open * 100
    print(f"FIRST OPEN: {first_open}   AFTER 15 OPEN: {after_15_open}")
    print(percentage_difference)
    
    
    

main()