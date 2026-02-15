import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Login | Crypto Analyzer", layout="centered")

st.title("🔐 Login")
st.subheader("Enter details to continue")

# ---------------- USER DATA FILE ----------------
USER_FILE = "users.csv"

# Create file if not exists
if not os.path.exists(USER_FILE):
    pd.DataFrame(columns=["Username", "Email", "Login Time"]).to_csv(USER_FILE, index=False)

# ---------------- LOGIN FORM ----------------
with st.form("login_form"):
    username = st.text_input("Username")
    email = st.text_input("Email ID")
    submit = st.form_submit_button("Login")

# ---------------- LOGIN LOGIC ----------------
if submit:
    if username.strip() == "" or email.strip() == "":
        st.error("Please enter both Username and Email")
    else:
        # Save user data
        df = pd.read_csv(USER_FILE)
        df.loc[len(df)] = [username, email, datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        df.to_csv(USER_FILE, index=False)

        # Store login session
        st.session_state["logged_in"] = True
        st.session_state["username"] = username

        st.success("Login successful! Redirecting...")
        st.switch_page("pages/dashboard.py")
