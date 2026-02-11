import requests
import pandas as pd
from datetime import datetime
import os

# Create data folder if it doesn't exist
if not os.path.exists("data"):
    os.makedirs("data")

# List of cryptocurrencies (CoinGecko IDs)
coins = {
    "bitcoin": "bitcoin",
    "ethereum": "ethereum",
    "solana": "solana",
    "cardano": "cardano",
    "dogecoin": "dogecoin"

    
}

# Loop through each cryptocurrency
for coin_name, coin_id in coins.items():

    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"

    params = {
        "vs_currency": "usd",
        "days": "30"
    }

    response = requests.get(url, params=params)
    data = response.json()

    prices = data["prices"]

    df = pd.DataFrame(prices, columns=["timestamp", "price"])

    df["date"] = df["timestamp"].apply(
        lambda x: datetime.fromtimestamp(x / 1000).strftime("%Y-%m-%d")
    )

    df = df[["date", "price"]]

    file_path = f"data/{coin_name}_price_30_days.csv"
    df.to_csv(file_path, index=False)

    print(f"{coin_name.capitalize()} data saved successfully!")