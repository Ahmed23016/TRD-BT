import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
def calculate_bollinger_bands(df, window=20, std_dev=2):

    df['MA'] = df['Close'].rolling(window=window).mean()
    df['rolling_std'] = df['Close'].rolling(window=window).std()
    

    df['BB_Upper'] = df['MA'] + (df['rolling_std'] * std_dev)
    df['BB_Lower'] = df['MA'] - (df['rolling_std'] * std_dev)
    

def calculate_macd(df, short_window=12, long_window=26, signal_window=9):
    df['EMA_12'] = df['Close'].ewm(span=short_window, adjust=False).mean()
    df['EMA_26'] = df['Close'].ewm(span=long_window, adjust=False).mean()
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['Signal_Line'] = df['MACD'].ewm(span=signal_window, adjust=False).mean()

def calculate_rsi(df, window=14):
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

def backtest_strategy(df,ticker):
    initial_balance = 500  
    balance = initial_balance
    position = 0
    buy_price = 0
    stok=0
    for i in range(len(df)):
        niga=df[("Close", ticker)].iloc[i]

        if (
            df['BB_Upper'].iloc[i] - df['BB_Lower'].iloc[i] <= 0.4 and  
            df['RSI'].iloc[i] < 50 and  
            position == 0  

        ):
            position = 1
            buy_price = niga
            stok=balance / buy_price

            print(f"Bought at {buy_price} ")
        if position == 1 and (niga- buy_price) * stok >20:
            balance += (niga - buy_price )* stok -7
            position = 0
            print(f"Sold {stok} shares ")
            print(f"Sold at {niga} . Balance: {balance}")

    return balance - initial_balance

def main():
    ticker = "TSLA"
    df = yf.download(ticker, period="max",interval="1d")

    calculate_bollinger_bands(df)
    df=df.iloc[20:]
    calculate_macd(df)
    calculate_rsi(df)
    profit = backtest_strategy(df,ticker)
    print(f"Total Profit: {profit:.2f}")

    plt.figure(figsize=(14, 7))
    plt.plot(df['Close'], label="Close Price", alpha=0.5)
    plt.fill_between(df.index, df['BB_Lower'], df['BB_Upper'], color='gray', alpha=0.3, label="Bollinger Bands")
    plt.title("Stock Price and Bollinger Bands")
    plt.legend()
    plt.show()

if __name__ == "__main__":
    main()


# data =yf.download("QBTS",period="max",interval="1m")