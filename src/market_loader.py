# src/market_loader.py
import yfinance as yf
import pandas as pd
from functools import lru_cache

@lru_cache(maxsize=128)
def fetch_price(ticker: str, start="2010-01-01") -> pd.Series:
    """
    Return a daily price series with the ticker as the Series name.
    Prefers 'Adj Close'; falls back to 'Close' when needed.
    """
    df = yf.download(ticker, start=start, progress=False)
    if df.empty:
        raise ValueError(f"No price data returned for {ticker}")

    # Prefer adjusted close; fallback to close
    if "Adj Close" in df.columns:
        series = df["Adj Close"].copy()
    elif "Close" in df.columns:
        series = df["Close"].copy()
    else:
        raise KeyError(f"Neither 'Adj Close' nor 'Close' found for {ticker}")

    series.name = ticker  # label the Series
    return series