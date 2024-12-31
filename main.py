import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from libs import calculate_adx,calculate_bollinger_bands,calculate_macd,calculate_rsi,calculate_volume_trend

def backtest_strategy(df, ticker):
    initial_balance = 500
    balance = initial_balance
    position = 0
    buy_price = 0
    stok = 0

    buy_points = []
    sell_points = []

    for i in range(len(df)):
        niga=df[("Close", ticker)].iloc[i]

        if (
            df['BB_Upper'].iloc[i] - df['BB_Lower'].iloc[i] <= 0.4 and
            df['RSI'].iloc[i] < 50 and
            position == 0 
        ):
            position = 1
            buy_price = niga
            stok = balance / buy_price
            buy_points.append((df.index[i], niga)) 
            print(f"Bought at {buy_price} ")

        if position == 1 and (niga - buy_price) * stok > 20:
            balance += (niga - buy_price) * stok - 5
            position = 0
            sell_points.append((df.index[i], niga)) 
            print(f"Sold {stok} shares ")
            print(f"Sold at {niga} . Balance: {balance}")

    return balance - initial_balance, buy_points, sell_points

def main():
    ticker = "INTZ"
    df = yf.download(ticker, period="max", interval="1m")

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

    today = pd.Timestamp(today)
    df = df[df.index.date == today.date()]
    print(df)

    calculate_bollinger_bands(df)
    df = df.iloc[20:]
    calculate_macd(df)
    calculate_rsi(df)

    profit, buy_points, sell_points = backtest_strategy(df, ticker)
    print(f"Total Profit: {profit:.2f}")

    plt.figure(figsize=(14, 7))
    plt.plot(df['Close'], label="Close Price", alpha=0.5)
    plt.fill_between(df.index, df['BB_Lower'], df['BB_Upper'], color='gray', alpha=0.3, label="Bollinger Bands")

    for point in buy_points:
        plt.scatter(point[0], point[1], color='green', label='Buy Signal', marker='^', alpha=1)

    for point in sell_points:
        plt.scatter(point[0], point[1], color='red', label='Sell Signal', marker='v', alpha=1)

    plt.title("Stock Price, Bollinger Bands, and Trade Signals")
    plt.legend()
    plt.show()

if __name__ == "__main__":
    main()
