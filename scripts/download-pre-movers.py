import requests
from bs4 import BeautifulSoup
import os 
import json

url="https://www.tradingview.com/markets/stocks-usa/market-movers-pre-market-gainers/"
try:
        response = requests.get(url)
        response.raise_for_status()
except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}Error: {e}")
def scrape_rows(soup):
    target_classes = {"row-RdUXZpkv", "listRow"}
    return soup.find_all("tr", class_=lambda c: c and target_classes == set(c.split()))


def scrape_ticker(soup):
    target_classes = {"apply-common-tooltip", "tickerNameBox-GrtoTeat", "tickerName-GrtoTeat"}
    return soup.find("a", class_=lambda c: c and target_classes == set(c.split()))

soup = BeautifulSoup(response.content, "html.parser")
rows = scrape_rows(soup)
tickers = [{"Symbol": scrape_ticker(i).text} for i in rows if scrape_ticker(i)]


output_dir = "./data"
os.makedirs(output_dir, exist_ok=True)

output_file = os.path.join(output_dir, "pre-movers.json")

with open(output_file, "w") as f:
        json.dump(tickers, f, indent=4)