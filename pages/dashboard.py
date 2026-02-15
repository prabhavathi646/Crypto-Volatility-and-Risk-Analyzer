import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import os
import requests

# ---------------- LIVE DATA FETCH FUNCTION ----------------
@st.cache_data(ttl=3600)
def fetch_live_data(coin_name):
    coin_map = {
        "Bitcoin": "bitcoin",
        "Ethereum": "ethereum",
        "Solana": "solana",
        "Cardano": "cardano",
        "Dogecoin": "dogecoin"
    }

    coin_id = coin_map.get(coin_name)

    if not coin_id:
        return None

    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": "30"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException:
        return None


    if "prices" not in data:
        return None

    df_live = pd.DataFrame(data["prices"], columns=["timestamp", "price"])
    df_live["date"] = pd.to_datetime(df_live["timestamp"], unit="ms")

    return df_live

# ---------------- LOGIN CHECK ----------------
if "logged_in" not in st.session_state:
    st.warning("Please login to access the dashboard")
    st.stop()

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Crypto Volatility & Risk Analyzer",
    layout="wide"
)

# ---------------- TITLE ----------------
import streamlit as st

# -------------------------------------------------
# PAGE TITLE
# -------------------------------------------------

st.title("📊 Crypto Volatility & Risk Analyzer")
st.caption("A beginner-friendly platform to understand cryptocurrency risk and volatility")

st.divider()

# -------------------------------------------------
# INTRODUCTION SECTION (2 COLUMN LAYOUT)
# -------------------------------------------------

col1, col2 = st.columns(2)

with col1:
    st.subheader("📌 What is Cryptocurrency?")
    st.write(
        "Cryptocurrency is a digital or virtual currency that uses cryptography "
        "for security and operates on decentralized blockchain networks."
    )

    st.subheader("📌 What is Volatility?")
    st.write(
        "Volatility refers to how much the price of a cryptocurrency fluctuates over time. "
        "High volatility means prices can rise or fall rapidly, increasing risk."
    )

with col2:
    st.subheader("📌 Why Risk Analysis is Important?")
    st.write(
        "Crypto markets are highly unpredictable. Risk analysis helps investors "
        "understand market uncertainty and make informed decisions."
    )

    st.info(
        "⚠️ High volatility = Higher risk\n\n"
        "✅ Risk analysis helps reduce uncertainty"
    )

st.divider()

# -------------------------------------------------
# LEARNING RESOURCES SECTION
# -------------------------------------------------

st.subheader("📘 Learn More About Cryptocurrency")

st.write(
    "If you are new to cryptocurrency, explore the following beginner-friendly resources:"
)

st.markdown("""
🔗 **[Investopedia – What is Cryptocurrency?](https://www.investopedia.com/terms/c/cryptocurrency.asp)**  
🔗 **[Coinbase – Crypto Basics](https://www.coinbase.com/learn/crypto-basics)**  
🔗 **[CoinMarketCap Alexandria – Crypto Education](https://coinmarketcap.com/alexandria/)**
""")

st.divider()

# -------------------------------------------------
# SYSTEM FEATURES SECTION
# -------------------------------------------------

st.subheader("🛠️ What Our System Does")

with st.expander("Click to see system capabilities"):
    st.markdown("""
    ✔ Fetches live and historical cryptocurrency price data  
    ✔ Calculates volatility and risk scores  
    ✔ Classifies crypto assets as **Stable**, **Alert**, or **Extreme**  
    ✔ Displays interactive charts and dashboards  
    ✔ Allows CSV & PDF export of analysis results  
    """)

st.success("✅ System is ready for analysis. Please proceed to the dashboard section.")

# ---------------- LOAD DATA ----------------
df = pd.read_csv("final_risk_analysis.csv")

# ---------------- COIN SELECTOR ----------------
st.subheader("🔍 Select Cryptocurrency")
coin_list = df["Coin"].tolist()
selected_coin = st.selectbox("Choose a coin to analyze:", coin_list)

selected_df = df[df["Coin"] == selected_coin]

# ---------------- SELECTED COIN DETAILS ----------------
st.subheader(f"📊 Risk Analysis for {selected_coin}")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Overall Volatility (%)", round(selected_df["Overall Volatility (%)"].values[0], 2))
col2.metric("Avg Rolling Volatility (%)", round(selected_df["Avg Rolling Volatility (%)"].values[0], 2))
col3.metric("Risk Score", round(selected_df["Risk Score"].values[0], 2))
col4.metric("Risk Level", selected_df["Risk Level"].values[0])


# =====================================================
# ✅ FIXED: CLEAN DAILY PRICE & VOLATILITY TREND
# =====================================================

st.subheader("📈 Price & Volatility Trends")

days = st.slider(
    "Select number of days to view",
    min_value=7,
    max_value=30,
    value=14
)

hist_df = fetch_live_data(selected_coin)

if hist_df is not None:

    # Convert to datetime
    hist_df["date"] = pd.to_datetime(hist_df["date"])

    # 🔥 Aggregate to DAILY data
    daily_df = (
        hist_df
        .groupby(hist_df["date"].dt.date)
        .agg({"price": "mean"})
        .reset_index()
    )

    daily_df.rename(columns={"date": "Date"}, inplace=True)
    daily_df = daily_df.tail(days)

    # Calculate rolling volatility
    daily_df["daily_return"] = daily_df["price"].pct_change()
    daily_df["rolling_volatility"] = (
        daily_df["daily_return"].rolling(window=3).std() * 100
    )

    # Plotly figure
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=daily_df["Date"],
            y=daily_df["price"],
            name="Price (USD)",
            mode="lines+markers",
            line=dict(width=3)
        )
    )

    fig.add_trace(
        go.Scatter(
            x=daily_df["Date"],
            y=daily_df["rolling_volatility"],
            name="Volatility (%)",
            mode="lines+markers",
            yaxis="y2",
            line=dict(width=3, dash="dot")
        )
    )

    fig.update_layout(
        template="plotly_dark",
        title=f"{selected_coin} Price & Volatility Trends",
        xaxis=dict(title="Date"),
        yaxis=dict(title="Price (USD)"),
        yaxis2=dict(
            title="Volatility (%)",
            overlaying="y",
            side="right"
        ),
        hovermode="x unified",
        height=450
    )

    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("Live data could not be fetched for the selected coin.")


# ---------------- RISK METRICS TABLE ----------------
st.subheader("📌 Risk Metrics Summary")

def color_risk_level(val):
    if val == "Stable":
        return "background-color: #2ecc71; color: black"
    elif val == "Alert":
        return "background-color: #f1c40f; color: black"
    else:
        return "background-color: #e74c3c; color: white"

styled_df = df.style.map(color_risk_level, subset=["Risk Level"])
st.dataframe(styled_df, use_container_width=True)

# ---------------- INTERACTIVE BAR CHART ----------------
st.subheader("📈 Risk Score Comparison ")

# Define color mapping for risk levels
risk_colors = {
    "Stable": "#2ecc71",
    "Alert": "#f1c40f",
    "Extreme": "#e74c3c"
}

fig = px.bar(
    df,
    x="Coin",
    y="Risk Score",
    color="Risk Level",
    color_discrete_map=risk_colors,
    text="Risk Score",
    title="Risk Score Comparison Across Cryptocurrencies",
    template="plotly_dark"
)

fig.update_traces(
    texttemplate='%{text:.2f}',
    textposition='outside'
)

fig.update_layout(
    xaxis_title="Cryptocurrency",
    yaxis_title="Risk Score",
    hovermode="x unified",
    height=450
)

st.plotly_chart(fig, use_container_width=True)

# =====================================================
# ✅ INTERACTIVE RISK–RETURN COMPARISON (PLOTLY)
# =====================================================

import plotly.express as px

st.subheader("⚖️ Risk–Return Analysis")

risk_return_data = []

for coin in df["Coin"]:
    temp_df = fetch_live_data(coin)

    if temp_df is not None:
        temp_df["date"] = pd.to_datetime(temp_df["date"])

        # Daily average price
        daily_df = (
            temp_df
            .groupby(temp_df["date"].dt.date)
            .agg({"price": "mean"})
            .reset_index()
        )

        # Daily returns
        daily_df["daily_return"] = daily_df["price"].pct_change()

        avg_return = daily_df["daily_return"].mean() * 100
        volatility = daily_df["daily_return"].std() * 100

        risk_return_data.append({
            "Coin": coin,
            "Return (%)": avg_return,
            "Volatility (%)": volatility
        })

# Create DataFrame
rr_df = pd.DataFrame(risk_return_data)

# 🔧 FIX: Bubble size must be positive
rr_df["Bubble Size"] = rr_df["Return (%)"].abs()

# ---------------- PLOTLY SCATTER ----------------
fig_rr = px.scatter(
    rr_df,
    x="Volatility (%)",
    y="Return (%)",
    color="Coin",
    size="Bubble Size",
    hover_name="Coin",
    template="plotly_dark",
    title="Risk–Return Comparison Across Cryptocurrencies",
    height=450
)

fig_rr.update_traces(
    marker=dict(
        line=dict(width=1, color="white"),
        sizemode="area",
        sizeref=2. * rr_df["Bubble Size"].max() / (40 ** 2),
        sizemin=8
    )
)

fig_rr.update_layout(
    xaxis_title="Volatility (%)",
    yaxis_title="Return (%)",
    hovermode="closest"
)

st.plotly_chart(fig_rr, use_container_width=True)

# =====================================================
# ✅ RISK CLASSIFICATION DASHBOARD (MILESTONE)
# =====================================================

st.subheader("🚦 Risk Classification Dashboard")

# Group data by Risk Level
high_risk = df[df["Risk Level"] == "Extreme"]
medium_risk = df[df["Risk Level"] == "Alert"]
low_risk = df[df["Risk Level"] == "Stable"]

# ---------------- RISK CARDS ----------------
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("### 🔴 High Risk")
    for _, row in high_risk.iterrows():
        st.markdown(f"**{row['Coin']}** — {row['Risk Score']:.2f}%")

with c2:
    st.markdown("### 🟡 Medium Risk")
    for _, row in medium_risk.iterrows():
        st.markdown(f"**{row['Coin']}** — {row['Risk Score']:.2f}%")

with c3:
    st.markdown("### 🟢 Low Risk")
    for _, row in low_risk.iterrows():
        st.markdown(f"**{row['Coin']}** — {row['Risk Score']:.2f}%")

st.divider()

# ---------------- RISK SUMMARY REPORT ----------------
st.subheader("📌 Risk Summary Report")

total_coins = len(df)
avg_risk = df["Risk Score"].mean()

col4, col5, col6 = st.columns(3)

col4.metric("Total Cryptocurrencies", total_coins)
col5.metric("Average Risk Score", f"{avg_risk:.2f}%")
col6.metric(
    "Risk Distribution",
    f"{len(high_risk)} High / {len(medium_risk)} Medium / {len(low_risk)} Low"
)

# ---------------- DONUT CHART ----------------
risk_dist_df = pd.DataFrame({
    "Risk Level": ["High", "Medium", "Low"],
    "Count": [len(high_risk), len(medium_risk), len(low_risk)]
})

fig_donut = px.pie(
    risk_dist_df,
    names="Risk Level",
    values="Count",
    hole=0.55,
    color="Risk Level",
    color_discrete_map={
        "High": "#e74c3c",
        "Medium": "#f1c40f",
        "Low": "#2ecc71"
    },
    title="Risk Distribution",
    template="plotly_dark"
)

st.plotly_chart(fig_donut, use_container_width=True)

# ---------------- EXPORT OPTIONS ----------------
st.subheader("📤 Export Results")

c7, c8 = st.columns(2)

with c7:
    st.download_button(
        "⬇ Download CSV",
        data=df.to_csv(index=False),
        file_name="final_risk_analysis.csv",
        mime="text/csv"
    )

# =====================================================
# ✅ FULL DASHBOARD PDF EXPORT (WITH VISUALS)
# =====================================================

from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from io import BytesIO
from datetime import datetime
import tempfile

st.subheader("📄 Download Full Dashboard Report (PDF)")

def generate_full_pdf(df, fig_rr, fig_donut, fig_bar):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph(
        "<b>Crypto Volatility & Risk Analyzer – Final Dashboard Report</b>",
        styles["Title"]
    ))

    elements.append(Paragraph(
        f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        styles["Normal"]
    ))

    elements.append(Paragraph("<br/>", styles["Normal"]))

    # -------- Risk Classification Summary --------
    elements.append(Paragraph("<b>Risk Classification Summary</b>", styles["Heading2"]))

    stable = df[df["Risk Level"] == "Stable"]["Coin"].tolist()
    alert = df[df["Risk Level"] == "Alert"]["Coin"].tolist()
    extreme = df[df["Risk Level"] == "Extreme"]["Coin"].tolist()

    elements.append(Paragraph(
        f"<b>Stable:</b> {', '.join(stable) if stable else 'None'}<br/>"
        f"<b>Alert:</b> {', '.join(alert) if alert else 'None'}<br/>"
        f"<b>Extreme:</b> {', '.join(extreme) if extreme else 'None'}",
        styles["Normal"]
    ))

    elements.append(Paragraph("<br/>", styles["Normal"]))


    # -------- Risk Metrics Table --------
    elements.append(Paragraph("<b>Final Risk Metrics</b>", styles["Heading2"]))

    table_data = [list(df.columns)] + df.values.tolist()
    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("BACKGROUND", (0,0), (-1,0), colors.darkgray),
        ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
    ]))
    elements.append(table)

    elements.append(Paragraph("<br/>", styles["Normal"]))

    # -------- Risk Score Comparison --------
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_bar:
        fig_bar.write_image(tmp_bar.name)
        elements.append(Paragraph("<b>Risk Score Comparison</b>", styles["Heading2"]))
        elements.append(Image(tmp_bar.name, width=400, height=300))

    elements.append(Paragraph("<br/>", styles["Normal"]))

    # -------- Save Plotly Charts as Images --------
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp1:
        fig_rr.write_image(tmp1.name)
        elements.append(Paragraph("<b>Risk–Return Comparison</b>", styles["Heading2"]))
        elements.append(Image(tmp1.name, width=400, height=300))

    elements.append(Paragraph("<br/>", styles["Normal"]))

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp2:
        fig_donut.write_image(tmp2.name)
        elements.append(Paragraph("<b>Risk Distribution</b>", styles["Heading2"]))
        elements.append(Image(tmp2.name, width=300, height=300))

    # Footer
    elements.append(Paragraph("<br/><br/>", styles["Normal"]))
    elements.append(Paragraph(
        "Internship Project | Crypto Volatility & Risk Analyzer",
        styles["Normal"]
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer

pdf_file = generate_full_pdf(df, fig_rr, fig_donut, fig)

st.download_button(
    "⬇ Download Complete Dashboard PDF",
    data=pdf_file,
    file_name="Crypto_Dashboard_Report.pdf",
    mime="application/pdf"
)
# ---------------- FOOTER ----------------

st.markdown("---")
st.caption("Internship Project | Crypto Volatility & Risk Analyzer")
