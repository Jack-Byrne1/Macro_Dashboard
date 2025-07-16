import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from src.fred_loader import fetch_series
from scipy.stats import zscore

st.set_page_config(page_title="Macro Growth Tracker", layout="wide")

# ---------- Load data ---------- #
@st.cache_data(show_spinner="Fetching FRED growth indicators...")
def load_growth_data():
    indicators = {
        "Industrial Production": "INDPRO",
        "Retail Sales ex Autos/Gas": "RSXFS",
        "Nonfarm Payrolls": "PAYEMS",
        "Initial Jobless Claims": "ICSA",
        "Real GDP": "GDPC1",
        "CFNAI Index": "CFNAI"
    }

    dfs = {}

    for label, code in indicators.items():
        series = fetch_series(code)

        # GDP is quarterly — convert to YoY %
        if code == "GDPC1":
            series = series.resample("Q").last()
            yoy = series.pct_change(4) * 100
            yoy.name = label
            dfs[label] = yoy

        # Jobless claims — invert YoY %
        elif code == "ICSA":
            weekly = series.resample("W").last()
            monthly = weekly.resample("ME").mean()
            yoy = monthly.pct_change(12) * 100
            yoy = -yoy  # invert
            yoy.name = label
            dfs[label] = yoy

        # CFNAI is already a standardized index
        elif code == "CFNAI":
            monthly = series.resample("ME").last()
            monthly.name = label
            dfs[label] = monthly

        # Everything else — YoY %
        else:
            monthly = series.resample("ME").last()
            yoy = monthly.pct_change(12) * 100
            yoy.name = label
            dfs[label] = yoy

    df = pd.concat(dfs.values(), axis=1).dropna()
    z_df = df.apply(zscore, nan_policy='omit')
    z_df["Composite Growth Score"] = z_df.mean(axis=1)

    return df, z_df

# ---------- Signal Logic ---------- #
def get_growth_signal(score):
    if score < -1.0:
        return "🔴 Contraction Risk"
    elif score < 0.5:
        return "🟡 Slowing Growth"
    else:
        return "🟢 Expansion Momentum"

# ---------- Render UI ---------- #
def render():
    st.title("📈 Macro Dashboard: Growth Tracker")

    raw_df, z_df = load_growth_data()
    latest_score = z_df["Composite Growth Score"].iloc[-1]
    latest_date = z_df.index[-1].strftime("%b %Y")
    signal = get_growth_signal(latest_score)

    st.metric(
        label=f"Growth Signal ({latest_date})",
        value=f"{latest_score:.2f} z-score",
        delta=signal
    )

    # Plot
    fig = go.Figure()
    for col in z_df.columns[:-1]:
        fig.add_trace(go.Scatter(x=z_df.index, y=z_df[col], mode="lines",
                                 name=col, line=dict(width=1.5, dash="dot")))

    fig.add_trace(go.Scatter(x=z_df.index, y=z_df["Composite Growth Score"],
                             mode="lines", name="Composite Score", line=dict(width=3)))

    fig.update_layout(
        title="Z-Score Normalized Growth Indicators",
        yaxis_title="Standard Deviations",
        legend_title="Series",
        height=500,
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("📊 Show Latest Z-Scores"):
        st.dataframe(z_df.tail(12).style.format("{:.2f}"))

# ---------- Run ---------- #
if __name__ == "__main__":
    render()
