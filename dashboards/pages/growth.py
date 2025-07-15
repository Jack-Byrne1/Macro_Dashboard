import streamlit as st
import plotly.express as px
from src.fred_loader import fetch_series

def render():
    st.header("Growth & Inflation")

    series_map = {
        "GDP (US, real)": "GDPC1",
        "CPI (US)": "CPIAUCSL"
    }
    default_pick = list(series_map.keys())
    picks = st.multiselect("Select indicators", series_map.keys(), default=default_pick)

    if not picks:
        st.info("Pick at least one series.")
        return

    # Fetch and combine
    dfs = [fetch_series(series_map[p]).rename(columns={series_map[p]: p}) for p in picks]
    data = dfs[0].join(dfs[1:], how="outer").dropna()

    # Plot
    fig = px.line(data, x=data.index, y=data.columns, title="Growth & Inflation Indicators")
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    render()