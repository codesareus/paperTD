import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import pytz
import requests

# Finnhub API key
FINNHUB_API_KEY = "cgtch1hr01qoiqvovb4gcgtch1hr01qoiqvovb50"  # Replace with your actual Finnhub API key

# Function to fetch stock data from Finnhub API
def fetch_stock_data_finnhub(ticker, interval="1", start_time=None, end_time=None):
    """
    Fetches stock data from Finnhub API.
    :param ticker: Stock ticker symbol (e.g., "AAPL")
    :param interval: Time interval in minutes ("1", "5", "30")
    :param start_time: Start time in UNIX timestamp
    :param end_time: End time in UNIX timestamp
    :return: DataFrame with stock data
    """
    if not start_time or not end_time:
        # Default to last 5 days of data

        # Get current time in UTC
        end_time = int(datetime.utcnow().timestamp())  # Ensure it's in UTC
        start_time = int((datetime.utcnow() - timedelta(days=5)).timestamp())  # 5 days ago

        st.write(f"Start Time: {start_time}, End Time: {end_time}")  # Debug
        #end_time = int(datetime.now().timestamp())
        #start_time = int((datetime.now() - timedelta(days=5)).timestamp())

    url = f"https://finnhub.io/api/v1/stock/candle?symbol={ticker}&resolution={interval}&from={start_time}&to={end_time}&token={FINNHUB_API_KEY}"
    response = requests.get(url)

    st.write(response.status_code, response.text)  # Print full response
    
    if response.status_code != 200:
        st.error(f"Failed to fetch data for {ticker}. Please check the ticker and try again.")
        return pd.DataFrame()

    data = response.json()
    if data.get("s") != "ok":
        st.error(f"No data available for {ticker}. Please check the ticker and try again.")
        return pd.DataFrame()

    df = pd.DataFrame({
        "Time": pd.to_datetime(data["t"], unit="s"),
        "Open": data["o"],
        "High": data["h"],
        "Low": data["l"],
        "Close": data["c"],
        "Volume": data["v"]
    })
    df.set_index("Time", inplace=True)
    return df


# Streamlit app
def main():
    st.title("finnhub")
    end_time = int(datetime.now().timestamp())
    start_time = int((datetime.now() - timedelta(days=5)).timestamp())

    st.write(f"Start Time: {start_time}, End Time: {end_time}")

    # Input box for user to enter stock ticker
    ticker = st.text_input("Enter Stock Ticker (e.g., SPY, AAPL, TSLA):", value="SPY").upper()

    # Add a button group for interval selection
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("1 Minute"):
            interval = "1"
    with col2:
        if st.button("5 Minutes", key="5m"):
            interval = "5"
    with col3:
        if st.button("30 Minutes", key="30m"):
            interval = "30"

    # Default interval
    if 'interval' not in locals():
        interval = "1"

    # Add a button to refresh data
    if st.button("Refresh Data"):
        st.cache_data.clear()  # Clear cached data to force a fresh fetch

    # Fetch data for the user-specified stock and interval
    data = fetch_stock_data_finnhub(ticker, interval=interval)
    if data.empty:
        st.error(f"Failed to fetch data for {ticker}. Please check the ticker and try again.")
        return

    # Add a slider for backtracking
    

    # Adjust the data based on the selected backtrack
    data_recent = data.tail(300 )  # Get the most recent 300 + selected_backtrack data points
    st.write(data_recent.tail(5))

    # Get the current price (last available price in the data)
    current_price = data_recent['Close'].iloc[-1]
    st.write(current_price)
    # Fetch the previous day's close price
    
if __name__ == "__main__":
    main()

