import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from libs import calculate_adx, calculate_bollinger_bands, calculate_macd, calculate_rsi, calculate_volume_trend

def bcktst_strtgy(df, tckr):
    ntl_blnc = 500
    blnc = ntl_blnc
    pstn = 0
    by_prc = 0
    stk = 0
    by_pnts = []
    sll_pnts = []
    for x in range(len(df)):
        pr = df[("Close", tckr)].iloc[x]
        if (
            df['BB_Upper'].iloc[x] - df['BB_Lower'].iloc[x] <= 0.4 and
            df['RSI'].iloc[x] < 50 and
            pstn == 0
        ):
            pstn = 1
            by_prc = pr
            stk = blnc / by_prc
            by_pnts.append((df.index[x], pr))
            print(f"Bght t {by_prc}")
        if pstn == 1 and (pr - by_prc) * stk > 20:
            blnc += (pr - by_prc) * stk - 5
            pstn = 0
            sll_pnts.append((df.index[x], pr))
            print(f"Sld {stk} shrs")
            print(f"Sld t {pr} Blnc: {blnc}")
    return blnc - ntl_blnc, by_pnts, sll_pnts

def mn():
    tckr = "INTZ"
    df = yf.download(tckr, period="max", interval="1m")
    df.index = pd.to_datetime(df.index)
    df = df.reset_index()
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    df.set_index('Datetime', inplace=True)
    td = datetime.now().date()
    if td.weekday() == 5:
        td = td - timedelta(days=1)
    elif td.weekday() == 6:
        td = td - timedelta(days=2)
    td = pd.Timestamp(td)
    df = df[df.index.date == td.date()]
    print(df)
    calculate_bollinger_bands(df)
    df = df.iloc[20:]
    calculate_macd(df)
    calculate_rsi(df)
    prft, by_pnts, sll_pnts = bcktst_strtgy(df, tckr)
    print(f"TTl Prft: {prft:.2f}")
    plt.figure(figsize=(14, 7))
    plt.plot(df['Close'], label="Cls", alpha=0.5)
    plt.fill_between(df.index, df['BB_Lower'], df['BB_Upper'], color='gray', alpha=0.3, label="BB")
    for p in by_pnts:
        plt.scatter(p[0], p[1], color='green', marker='^')
    for p in sll_pnts:
        plt.scatter(p[0], p[1], color='red', marker='v')
    plt.title("Prc BB Trd")
    plt.legend()
    plt.show()

if __name__ == "__main__":
    mn()
