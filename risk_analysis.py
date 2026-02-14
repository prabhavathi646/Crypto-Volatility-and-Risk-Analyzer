import pandas as pd
import requests
from datetime import datetime

# -------------------------------------------------
# STEP 0: COINS TO ANALYZE (CoinGecko IDs)
# -------------------------------------------------

coins = {
    "Bitcoin": "bitcoin",
    "Ethereum": "ethereum",
    "Solana": "solana",
    "Cardano": "cardano",
    "Dogecoin": "dogecoin"
}

results = []

# -------------------------------------------------
# STEP 1: FETCH LIVE DATA FUNCTION
# -------------------------------------------------

def fetch_live_data(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    
    params = {
        "vs_currency": "usd",
        "days": "30"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Error fetching data for {coin_id}: {e}")
        return None

    if "prices" not in data or len(data["prices"]) == 0:
        return None

    prices = data["prices"]

    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["date"] = pd.to_datetime(df["timestamp"], unit="ms")

    return df


# -------------------------------------------------
# STEP 2: CALCULATE RISK SCORES
# -------------------------------------------------

for coin_name, coin_id in coins.items():

    df = fetch_live_data(coin_id)

    if df is None:
        print(f"Skipping {coin_name} (No data found)")
        continue

    # Daily return
    df["daily_return"] = df["price"].pct_change()

    # Overall volatility
    overall_volatility = df["daily_return"].std() * 100

    # Rolling volatility (7-day)
    df["rolling_volatility"] = df["daily_return"].rolling(window=7).std() * 100
    avg_rolling_volatility = df["rolling_volatility"].mean()

    # Custom Risk Score
    risk_score = (overall_volatility * 0.6) + (avg_rolling_volatility * 0.4)

    results.append({
        "Coin": coin_name,
        "Overall Volatility (%)": round(overall_volatility, 2),
        "Avg Rolling Volatility (%)": round(avg_rolling_volatility, 2),
        "Risk Score": round(risk_score, 2)
    })

# Convert to DataFrame
final_df = pd.DataFrame(results)

# ✅ SAFETY CHECK (prevents crash)
if final_df.empty:
    print("No data available. Risk analysis cannot be performed.")
    exit()

# -------------------------------------------------
# STEP 3: DYNAMIC RISK CLASSIFICATION (PERCENTILES)
# -------------------------------------------------

risk_scores = final_df["Risk Score"]

low_threshold = risk_scores.quantile(0.30)
high_threshold = risk_scores.quantile(0.70)

def classify_dynamic_risk(score):
    if score <= low_threshold:
        return "Stable"
    elif score <= high_threshold:
        return "Alert"
    else:
        return "Extreme"

final_df["Risk Level"] = final_df["Risk Score"].apply(classify_dynamic_risk)

# -------------------------------------------------
# STEP 4: SAVE RESULTS
# -------------------------------------------------

final_df.to_csv("final_risk_analysis.csv", index=False)

print("Final risk classification completed successfully!")
print(final_df)

