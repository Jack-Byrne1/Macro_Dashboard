import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from src.market_loader import fetch_price

TICKERS = {
    "S&P 500 (SPY)": "SPY",
    "US 20Y Treasuries (TLT)": "TLT",
    "Gold (GLD)": "GLD",
    "Oil (USO)": "USO",
    "USD Index (DX)": "DX-Y.NYB",
    "Bitcoin (BTC)": "BTC-USD",
    "High‑Yield Credit (HYG)": "HYG",
}

@st.cache_data(show_spinner="Fetching prices…")
def load_prices():
    dfs = [fetch_price(tkr) for tkr in TICKERS.values()]
    return pd.concat(dfs, axis=1).dropna()

def render():
    st.header("Cross‑Asset Correlation Heat‑Map")

    lookback = st.slider("Look‑back window (days)", 30, 365, 180, step=30)
    prices = load_prices()

    # Log‑returns
    rets = (prices / prices.shift(1)).apply(np.log).dropna()
    corr = rets.tail(lookback).corr()

    # Plotly heat‑map
    fig = px.imshow(
        corr,
        text_auto=".2f",
        color_continuous_midpoint=0,
        color_continuous_scale="RdBu_r",
        title=f"{lookback}-Day Rolling Correlation"
    )
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Correlation table"):
        st.dataframe(corr.style.format("{:.2f}"))

if __name__ == "__main__":
    render()