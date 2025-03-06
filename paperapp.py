import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
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
        end_time = int(datetime.now().timestamp())
        start_time = int((datetime.now() - timedelta(days=5)).timestamp())

    url = f"https://finnhub.io/api/v1/stock/candle?symbol={ticker}&resolution={interval}&from={start_time}&to={end_time}&token={FINNHUB_API_KEY}"
    response = requests.get(url)
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

# Function to fetch daily close prices for the last 5 days
def fetch_daily5_finnhub(ticker):
    """
    Fetches the last 5 days of daily close prices from Finnhub API.
    :param ticker: Stock ticker symbol (e.g., "AAPL")
    :return: Series of close prices
    """
    end_time = int(datetime.now().timestamp())
    start_time = int((datetime.now() - timedelta(days=5)).timestamp())
    url = f"https://finnhub.io/api/v1/stock/candle?symbol={ticker}&resolution=D&from={start_time}&to={end_time}&token={FINNHUB_API_KEY}"
    response = requests.get(url)
    if response.status_code != 200:
        st.error(f"Failed to fetch daily data for {ticker}. Please check the ticker and try again.")
        return None

    data = response.json()
    if data.get("s") != "ok":
        st.error(f"No data available for {ticker}. Please check the ticker and try again.")
        return None

    df = pd.DataFrame({
        "Time": pd.to_datetime(data["t"], unit="s"),
        "Close": data["c"]
    })
    df.set_index("Time", inplace=True)
    return df["Close"]

# Function to fetch the previous day's close price
def fetch_previous_close(ticker):
    close_prices = fetch_daily5(ticker)
    if close_prices is None:
        return None  # Handle cases where there isn't enough data
    
    # Get current time in NY (US Eastern Time)
    midwest = pytz.timezone("America/chicago")
    now = datetime.now(midwest)  # Use datetime from the imported module
    
    # Define US market hours
    market_open = now.replace(hour=8, minute=30, second=0, microsecond=0)
    market_close = now.replace(hour=15, minute=0, second=0, microsecond=0)
    
    if now < market_open or now > market_close:  # Pre-market or post-market
        previous_close = close_prices[-1]  # Use the previous day's close
    else:
        previous_close = close_prices[-2]  # Use the most recent close
    
    return previous_close
# Function to fetch the day before yesterday's close price
def fetch_d2_close_finnhub(ticker):
    close_prices = fetch_daily5_finnhub(ticker)
    if close_prices is None or len(close_prices) < 3:
        return None  # Handle cases where there isn't enough data

    # Get current time in NY (US Eastern Time)
    midwest = pytz.timezone("America/chicago")
    now = datetime.now(midwest)

    # Define US market hours
    market_open = now.replace(hour=8, minute=30, second=0, microsecond=0)
    market_close = now.replace(hour=15, minute=0, second=0, microsecond=0)

    if now < market_open or now > market_close:  # Pre-market or post-market
        d2_close = close_prices[-2]  # Use the previous day's close
    else:
        d2_close = close_prices[-3]  # Use the most recent close

    return d2_close

# Rest of the code remains unchanged...

# Streamlit app
def main():
    st.title("Stock Price Regression Analysis")
    st.write("This app fetches stock prices at different intervals (including premarket data) and performs linear and polynomial regression analysis.")

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
        interval = "5"

    # Add a button to refresh data
    if st.button("Refresh Data"):
        st.cache_data.clear()  # Clear cached data to force a fresh fetch

    # Fetch data for the user-specified stock and interval
    data = fetch_stock_data_finnhub(ticker, interval=interval)
    if data.empty:
        st.error(f"Failed to fetch data for {ticker}. Please check the ticker and try again.")
        return

    # Add a slider for backtracking
    backtrack_options = [0, 2, 5, 7, 10, 20, 30, 45, 60, 90, 100, 120]
    selected_backtrack = st.slider(
        "Select number of points to backtrack:",
        min_value=min(backtrack_options),
        max_value=max(backtrack_options),
        value=0,  # Default value
        step=1,  # Step size
        key="backtrack_slider"
    )

    # Adjust the data based on the selected backtrack
    data_recent = data.tail(300 + selected_backtrack)  # Get the most recent 300 + selected_backtrack data points
    data_recent = data_recent.head(300)  # Use only the first 300 points after backtracking

    # Get the current price (last available price in the data)
    current_price = data_recent['Close'].iloc[-1]

    # Fetch the previous day's close price
    previous_close = fetch_previous_close_finnhub(ticker)
    if previous_close is None:
        st.error("Failed to fetch the previous day's close price. Please try again.")
        return

    change = current_price - previous_close

    # Calculate percentage change
    percentage_change = calculate_percentage_change(current_price, previous_close)

    # Get current local time
    midwest = pytz.timezone("America/chicago")
    current_time = datetime.now(midwest).strftime("%H:%M:%S")

    # Display the percentage change message with current local time
    st.write("### Current Price vs Previous Close___" f"{ticker}")
    if percentage_change >= 0:
        st.success(f"🟢 {ticker}:  **{current_price:.2f}**, **{change:.2f}**  (**{percentage_change:.2f}%**, previous_close **{previous_close:.2f}**)  |	{current_time}	")
    else:
        st.error(f"🔴 {ticker}:  **{current_price:.2f}**, **{change:.2f}**  (**{percentage_change:.2f}%**, prev_close **{previous_close:.2f}**)  |	{current_time}	")

    # Perform linear regression (using only the most recent 300 points)
    X, y, y_pred_linear, r2_linear, data_recent = perform_regression(data_recent, degree=1)

    # Add buttons for polynomial degree selection
    st.write("### Polynomial Regression Analysis")
    col_deg2, col_deg3 = st.columns(2)
    with col_deg2:
        if st.button("Degree 2"):
            degree = 2
    with col_deg3:
        if st.button("Degree 3"):
            degree = 3

    # Default degree
    if 'degree' not in locals():
        degree = 3  # Default to degree 3

    # Display the current polynomial degree
    st.write(f"**Current Polynomial Degree:** {degree}")

    # Perform polynomial regression with the selected degree
    X, y, y_pred_poly, r2_poly, _ = perform_regression(data_recent, degree=degree)

    # Calculate residuals and standard deviation for the polynomial model
    residuals = y - y_pred_poly
    std_dev = np.std(residuals)

    # Calculate exponential moving averages
    data_recent['EMA_9'] = data_recent['Close'].ewm(span=9, adjust=False).mean()
    data_recent['EMA_20'] = data_recent['Close'].ewm(span=20, adjust=False).mean()

    # Determine the trend message
    if current_price > data_recent['EMA_9'].iloc[-1] and data_recent['EMA_9'].iloc[-1] > data_recent['EMA_20'].iloc[-1]:
        trend_message = f"Trend UP"
        trend_color = "green"
    elif current_price < data_recent['EMA_9'].iloc[-1] and data_recent['EMA_9'].iloc[-1] < data_recent['EMA_20'].iloc[-1]:
        trend_message = f"Trend DOWN"
        trend_color = "red"
    else:
        trend_message = f"Trend NEUTRAL"
        trend_color = "gray"

    # Extract time (hours and minutes) for the x-axis
    time_labels = data_recent.index.strftime('%H:%M')  # Format time as HH:MM

    # Simplify x-axis labels based on the interval
    if interval == "30":
        # For 30-minute interval, show only every 3 hours (e.g., 09:00, 12:00, 15:00)
        simplified_time_labels = [label if label.endswith('00') and int(label.split(':')[0]) % 3 == 0 else '' for label in time_labels]
    else:
        # For 1-minute and 5-minute intervals, show only hours (e.g., 09:00, 10:00)
        simplified_time_labels = [label if label.endswith('00') else '' for label in time_labels]

    # ... (rest of the code remains the same until the plotting section)

if __name__ == "__main__":
    main()

