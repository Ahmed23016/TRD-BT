import requests
from bs4 import BeautifulSoup
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from tabulate import tabulate
from colorama import Fore, Style, init

init(autoreset=True)

budget = 1000
results = []  
previous_close_changes = [] 


def get_premarket_stocks():
    global budget, results, previous_close_changes
    url = "https://www.tradingview.com/markets/stocks-usa/market-movers-pre-market-gainers/"
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}Error: {e}")
        return

    soup = BeautifulSoup(response.content, "html.parser")
    rows = scrape_rows(soup)
    tickers = [scrape_ticker(i).text for i in rows]
    before_budget = budget
    total_tickers = len(tickers)
    successful_trades = 0

    print(f"{Fore.CYAN}Analyzing {total_tickers} tickers...\n")
    for ticker in tickers:
        result = calc_perc_diff(ticker)
        if result == 2:
            successful_trades += 1
        elif result == False:
            total_tickers -= 1

    percentage_gain = (successful_trades / total_tickers) * 100
    print(f"{Fore.YELLOW}\nSummary:\n{'='*40}")
    print(f"{Fore.GREEN}Initial Budget: {before_budget:.2f}")
    print(f"{Fore.GREEN}Final Budget: {budget:.2f}")
    print(f"{Fore.GREEN}Total Successful Trades: {successful_trades} / {total_tickers}")
    print(f"{Fore.GREEN}Percentage Gain: {percentage_gain:.2f}%")
    print(f"{Fore.GREEN}Balance Increase: {abs(budget - before_budget) / before_budget * 100:.2f}%")

    if previous_close_changes:
        avg_close_open_change = sum(previous_close_changes) / len(previous_close_changes)
        print(f"{Fore.GREEN}Average Change (Last Close to Today’s Open): {avg_close_open_change:.2f}%")

    if results:
        results_sorted = sorted(results, key=lambda x: x["Percentage Change"], reverse=True)
        top_performer = results_sorted[0]
        worst_performer = results_sorted[-1]
        print(f"\n{Fore.BLUE}Top Performer: {top_performer['Ticker']} (+{top_performer['Percentage Change']:.2f}%)")
        print(f"{Fore.RED}Worst Performer: {worst_performer['Ticker']} ({worst_performer['Percentage Change']:.2f}%)")

        print(f"\n{Fore.BLUE}Top Performers:")
        print(tabulate(results_sorted[:3], headers="keys", tablefmt="fancy_grid", floatfmt=".2f"))
        print(f"\n{Fore.RED}Worst Performers:")
        print(tabulate(results_sorted[-3:], headers="keys", tablefmt="fancy_grid", floatfmt=".2f"))


def scrape_rows(soup):
    target_classes = {"row-RdUXZpkv", "listRow"}
    return soup.find_all("tr", class_=lambda c: c and target_classes == set(c.split()))


def scrape_ticker(soup):
    target_classes = {"apply-common-tooltip", "tickerNameBox-GrtoTeat", "tickerName-GrtoTeat"}
    return soup.find("a", class_=lambda c: c and target_classes == set(c.split()))


def get_data(symbol):
    return yf.download(symbol, period="5d", interval="1m")


def get_colums(df, column,ticker, index):
    try:
        return df[(column,ticker)].iloc[index]
    except IndexError:
        return None

def get_yesterday_close(df,ticker):
    yesterday = datetime.now() - timedelta(1)
    datetime.strftime(yesterday, '%Y-%m-%d')
    yesterday=pd.Timestamp(yesterday)
    yesterday_data=df[df.index.date == yesterday.date()]
    return get_colums(yesterday_data,"Close",ticker,-1)
def calc_stock(budget,stokprice):
    amount_stok=budget/stokprice
    return amount_stok

def calc_perc_diff(ticker):
    global budget, results, previous_close_changes
    previous_budget = budget

    try:
        df = get_data(ticker)
        if df is None or df.empty:
            print(f"{Fore.RED}No data available for {ticker}. Skipping...\n")
            return False

        df.index = pd.to_datetime(df.index)
        today = datetime.now().date()
        if today.weekday() in [5, 6]:
            today -= timedelta(days=(today.weekday() - 4))

        today_data = df[df.index.date == today]
        if today_data.empty:
            print(f"{Fore.RED}No data for today ({today}) for {ticker}. Skipping...\n")
            return False

        first_open = get_colums(today_data, "Close",ticker, 0)
        after_15_open = get_colums(today_data, "Open",ticker, 15)
        if first_open is None or after_15_open is None:
            print(f"{Fore.RED}Missing data for {ticker}. Skipping...\n")
            return False

        prev_close = get_yesterday_close(df,ticker) if not df.empty else None
        if prev_close is not None:
            close_open_change = ((first_open - prev_close) / prev_close) * 100
            previous_close_changes.append(close_open_change)
        else:
            close_open_change = None

        if first_open < 1:
            print(f"{Fore.RED}Skipping {ticker} as its open price is below $1.00.\n")
            return False

        percentage_difference = ((after_15_open - first_open) / first_open) * 100
        potential_new_budget = budget + (after_15_open - first_open) * (budget / first_open) - 5

        if percentage_difference <= 5:
            print(f"{Fore.RED}Not performing a trade with {ticker}. Change is not enough. Skipping...\n")
            return False

        budget = potential_new_budget

        results.append({
            "Ticker": ticker,
            "First Open": first_open,
            "After 15 Min Open": after_15_open,
            "Percentage Change": percentage_difference,
            "Close to Open Change": close_open_change,
            "Budget profit.(%)":(abs(budget - previous_budget) / previous_budget * 100),
            "Previous budget":previous_budget,
            "Current budget": budget,
        })

        print(f"{Fore.GREEN}Ticker: {ticker}")
        print(f"  {Style.BRIGHT}First Open: {first_open:.2f}")
        print(f"  {Style.BRIGHT}After 15 Min Open: {after_15_open:.2f}")
        print(f"  {Style.BRIGHT}Percentage Change: {percentage_difference:.2f}%")
        if close_open_change is not None:
            print(f"  {Style.BRIGHT}Close to Open Change: {close_open_change:.2f}%")
        print(f"  {Style.BRIGHT}Updated Budget: {budget:.2f}\n")

        return 2 if percentage_difference > 0 else 1

    except Exception as e:
        print(f"{Fore.RED}An error occurred with {ticker}: {e}. Restoring previous budget.")
        budget = previous_budget
        return False

get_premarket_stocks()
