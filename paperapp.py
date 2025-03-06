
import streamlit as st
import requests

# Set your Finnhub API key here
# Finnhub API key
FINNHUB_API_KEY = "cgtch1hr01qoiqvovb4gcgtch1hr01qoiqvovb50"  # Replace with your actual Finnhub API key

# Finnhub API endpoint for stock quote
FINNHUB_URL = "https://finnhub.io/api/v1/quote"

def fetch_stock_price(symbol):
    """Fetch the current stock price using Finnhub API."""
    params = {
        "symbol": symbol,
        "token": FINNHUB_API_KEY
    }
    response = requests.get(FINNHUB_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        return data.get("c")  # Current price
    else:
        st.error("Failed to fetch data. Please check the stock symbol or try again later.")
        return None

from datetime import datetime, timedelta

# Set your Finnhub API key here

# Finnhub API endpoint for extended market data (candles)
FINNHUB_CANDLE_URL = "https://finnhub.io/api/v1/stock/candle"

def fetch_premarket_price(symbol):
    """Fetch premarket price using Finnhub's candle endpoint."""
    # Get the current date and time
    now = datetime.utcnow()
    # Premarket hours typically start at 4:00 AM UTC (for US markets)
    premarket_start = now.replace(hour=4, minute=0, second=0, microsecond=0)
    
    # If the current time is before 4:00 AM UTC, use the previous day's premarket data
    if now < premarket_start:
        premarket_start -= timedelta(days=1)
    
    # Convert to timestamps (Finnhub uses Unix timestamps in seconds)
    from_timestamp = int(premarket_start.timestamp())
    to_timestamp = int(now.timestamp())

    params = {
        "symbol": symbol,
        "resolution": "1",  # 1-minute resolution
        "from": from_timestamp,
        "to": to_timestamp,
        "token": FINNHUB_API_KEY
    }

    response = requests.get(FINNHUB_CANDLE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        if data.get("s") == "ok":
            # Get the latest premarket price (last closing price in the premarket period)
            prices = data.get("c", [])
            if prices:
                return prices[-1]  # Last price in the premarket period
        else:
            st.error("No premarket data available for this symbol.")
    else:
        st.error("Failed to fetch data. Please check the stock symbol or try again later.")
    return None

def main():
    st.title("Premarket Stock Price Fetcher")
    st.write("Fetch the premarket price of any stock using Finnhub API.")

    # Input for stock symbol
    symbol = st.text_input("Enter Stock Symbol (e.g., AAPL):").upper()

    if st.button("Get Premarket Price"):
        if symbol:
            price = fetch_premarket_price(symbol)
            if price:
                st.success(f"The premarket price of {symbol} is ${price:.2f}")
        else:
            st.warning("Please enter a valid stock symbol.")

    st.title("Stock Price Fetcher")
    st.write("Fetch the current price of any stock using Finnhub API.")

    # Input for stock symbol
    symbol = st.text_input("Enter Stock Symbol (e.g., AAPL):").upper()

    if st.button("Get Price"):
        if symbol:
            price = fetch_stock_price(symbol)
            if price:
                st.success(f"The current price of {symbol} is ${price:.2f}")
        else:
            st.warning("Please enter a valid stock symbol.")

if __name__ == "__main__":
    main()

