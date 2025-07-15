import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
from src.market_loader import fetch_price

# ---------- UI ---------- #
st.header("Cumulative Return Chart")

UNIVERSE = ["SPY", "TLT", "GLD", "USO", "DX-Y.NYB", "BTC-USD", "HYG"]
tickers = st.multiselect(
    "Select up to 6 tickers (Yahoo symbols):",
    UNIVERSE, default=["SPY", "TLT", "GLD"], max_selections=6
)

if not tickers:
    st.stop()

# ---------- Load prices once to discover date span ---------- #
@st.cache_data(show_spinner="Fetching prices…")
def load_prices(selected):
    dfs = [fetch_price(t) for t in selected]
    return pd.concat(dfs, axis=1).dropna()

prices_full = load_prices(tuple(tickers))

# Slider: earliest valid date to today
min_date = prices_full.index.min().date()
max_date = prices_full.index.max().date()

start = st.slider(
    "Start date",
    min_value=min_date,
    max_value=max_date,
    value=min_date,               # default at earliest
    format="YYYY-MM-DD"
)

# ---------- Filter + plot ---------- #
prices = prices_full.loc[str(start):]

cum = prices / prices.iloc[0] * 100
cum = cum.rename(columns=lambda x: x.upper())

fig = px.line(
    cum,
    labels={"value": "Indexed to 100", "index": "Date", "variable": "Ticker"},
    title=f"Cumulative Return (Start = {start})"
)
st.plotly_chart(fig, use_container_width=True)

with st.expander("Show data"):
    st.dataframe(cum.tail().style.format("{:.1f}"))

