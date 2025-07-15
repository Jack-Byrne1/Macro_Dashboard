import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import timedelta
from src.market_loader import fetch_price

# ---------- settings ---------- #
WINDOW_DAYS  = 90              # rolling window length
TICKERS = {
    "SPY"      : "SPY",
    "TLT"      : "TLT",
    "GLD"      : "GLD",
    "USO"      : "USO",
    "DX‑Y.NYB" : "DX-Y.NYB",
    "BTC‑USD"  : "BTC-USD",
    "HYG"      : "HYG"
}

@st.cache_data(show_spinner="Fetching prices…")
def load_prices():
    dfs = [fetch_price(tkr) for tkr in TICKERS.values()]
    return pd.concat(dfs, axis=1).dropna()

def render():
    st.header("Cross‑Asset Correlation Heat‑Map — Rolling 90 Days")

    prices = load_prices()

    # --- restrict to last WINDOW_DAYS*2 to keep animation snappy --- #
    end_date   = prices.index[-1]
    start_date = end_date - timedelta(days=WINDOW_DAYS*2)  # tiny buffer
    prices = prices.loc[start_date:end_date]

    returns = np.log(prices / prices.shift(1)).dropna()

    # --- build frames for the LAST 90 days, daily step --- #
    frames = []
    dates  = returns.index[-WINDOW_DAYS:]  # one frame per day in the last window
    for d in dates:
        window = returns.loc[d - timedelta(days=WINDOW_DAYS-1): d]
        corr   = window.tail(WINDOW_DAYS).corr()
        frames.append(corr)

    # --- create Plotly animation --- #
    latest_corr = frames[-1]
    fig = go.Figure(
        data=[go.Heatmap(
            z=latest_corr.values,
            x=latest_corr.columns,
            y=latest_corr.columns,
            zmin=-1, zmax=1,
            text=latest_corr.round(2).values,
            texttemplate="%{text}",
            colorbar=dict(title="ρ"),
            colorscale="RdBu_r",
            hovertemplate="%{y}↔%{x}<br>ρ=%{z:.2f}<extra></extra>"
        )],
        layout={
            "title": f"Rolling {WINDOW_DAYS}-Day Correlation — {dates[-1].date()} (latest)",
            "updatemenus": [{
                "type": "buttons",
                "buttons": [{
                    "label": "Play",
                    "method": "animate",
                    "args": [
                        None,
                        {
                            "frame": {"duration": 200, "redraw": True},
                            "transition": {"duration": 0},
                            "fromcurrent": True
                        }
                    ]
                }]
            }]
        },
        frames=[
            go.Frame(
                data=[go.Heatmap(
                    z=c.values,
                    x=c.columns,
                    y=c.columns,
                    zmin=-1, zmax=1,
                    text=c.round(2).values,
                    texttemplate="%{text}",
                    colorscale="RdBu_r"
                )],
                name=str(d.date()),
                layout={"title": f"Rolling {WINDOW_DAYS}-Day Correlation — {d.date()}"}
            )
            for c, d in zip(frames, dates)
        ]
    )

    st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    render()