import pandas as pd
import os

DATA_FOLDER = "data"
results = []

# -------------------------------------------------
# STEP 1: CALCULATE RISK SCORES FOR ALL COINS
# -------------------------------------------------

for file in os.listdir(DATA_FOLDER):
    if file.endswith(".csv"):
        coin_name = file.replace("_price_30_days.csv", "").capitalize()
        df = pd.read_csv(os.path.join(DATA_FOLDER, file))

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

# -------------------------------------------------
# STEP 2: DYNAMIC RISK CLASSIFICATION (PERCENTILES)
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
# STEP 3: SAVE RESULTS
# -------------------------------------------------

final_df.to_csv("final_risk_analysis.csv", index=False)

print("Final risk classification completed successfully!")
print(final_df)

