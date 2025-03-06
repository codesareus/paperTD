
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
    

# Your Finnhub API key
    API_KEY = FINNHUB_API_KEY

# Stock symbol (example: AAPL)
    symbol = "SPY"

# Finnhub API endpoint for real-time stock quote
    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={API_KEY}"

# Make the request
    response = requests.get(url)
    data = response.json()

# Extract premarket price (if available)
    premarket_price = data.get("pm", "No premarket data available")

    st.write(f"Premarket price for {symbol}: {premarket_price}")


if __name__ == "__main__":
    main()

