import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
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

def calculate_adx(df, window=14):
    df['High-Low'] = df['High'] - df['Low']
    df['High-Close'] = abs(df['High'] - df['Close'].shift(1))
    df['Low-Close'] = abs(df['Low'] - df['Close'].shift(1))
    df['TR'] = df[['High-Low', 'High-Close', 'Low-Close']].max(axis=1)
    df['+DM'] = np.where((df['High'] - df['High'].shift(1)) > (df['Low'].shift(1) - df['Low']), df['High'] - df['High'].shift(1), 0)
    df['-DM'] = np.where((df['Low'].shift(1) - df['Low']) > (df['High'] - df['High'].shift(1)), df['Low'].shift(1) - df['Low'], 0)
    df['+DM'] = df['+DM'].where(df['+DM'] > 0, 0)
    df['-DM'] = df['-DM'].where(df['-DM'] > 0, 0)
    df['TR'] = df['TR'].rolling(window=window).sum()
    df['+DI'] = (df['+DM'].rolling(window=window).sum() / df['TR']) * 100
    df['-DI'] = (df['-DM'].rolling(window=window).sum() / df['TR']) * 100
    df['DX'] = (abs(df['+DI'] - df['-DI']) / (df['+DI'] + df['-DI'])) * 100
    df['ADX'] = df['DX'].rolling(window=window).mean()

def calculate_volume_trend(df):
    df['Volume_Change'] = df['Volume'].pct_change()
    df['Trend'] = np.where(df['Close'] > df['Close'].shift(1), 'Uptrend', 'Downtrend')
