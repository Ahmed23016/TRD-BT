import json
from bs4 import BeautifulSoup
import requests
import os
from tqdm import tqdm

def main():
    alphabet = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
    base_url = "https://stock-screener.org/stock-list.aspx?alpha={}"
    stock_data = []

    for letter in tqdm(alphabet,desc="Fetching stocks per letter",unit="Letter"):
        url = base_url.format(letter)
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        tbody = soup.find("tbody")  
        if tbody:
            rows = tbody.find_all("tr")

            for row in rows:
                cols = row.find_all("td")
                if cols:
                    symbol = cols[0].text.strip()
                    stock_data.append({"Symbol": symbol})

        else:
            print(f"No data found for letter '{letter}'")

    output_dir = "./data"
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, "stock_symbols.json")

    with open(output_file, "w") as f:
        json.dump(stock_data, f, indent=4)

    print(f"Data saved to {output_file}")

if __name__ == "__main__":
    main()
