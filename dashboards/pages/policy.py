import streamlit as st
import plotly.express as px
from src.fred_loader import fetch_series

# ---------- Core logic ---------- #
@st.cache_data(show_spinner="Downloading FRED data…")
def load_policy_data():
    """Fetch 2-year, 10-year yields and NBER recessions; compute 10s-2s spread."""
    df2   = fetch_series("GS2").rename(columns={"GS2": "2-Year"})
    df10  = fetch_series("GS10").rename(columns={"GS10": "10-Year"})
    usrec = fetch_series("USREC").rename(columns={"USREC": "Recession"})  # 0/1 flag

    df = df2.join(df10, how="inner")
    df["10s-2s Spread"] = df["10-Year"] - df["2-Year"]
    df = df.join(usrec, how="left")
    return df.dropna()

# ---------- Page renderer ---------- #
def render():
    st.header("Monetary Policy: 10s-2s Yield-Curve Spread")

    df = load_policy_data()

    # --- KPI cards --- #
    latest = df.iloc[-1]
    col1, col2, col3 = st.columns(3)
    col1.metric("2-Year",  f"{latest['2-Year']:.2f} %", delta=None)
    col2.metric("10-Year", f"{latest['10-Year']:.2f} %", delta=None)
    col3.metric("10s-2s", f"{latest['10s-2s Spread']:.2f} %", delta=None)

    # --- Line chart --- #
    fig = px.line(
        df,
        x=df.index,
        y=["2-Year", "10-Year", "10s-2s Spread"],
        title="US Treasury Yields & Term-Premium Spread",
        labels={"value": "Yield (%)", "variable": "Series"}
    )
    fig.update_yaxes(title="Yield / Spread (pct-points)")

    # --- Shade NBER recessions --- #
    recessions = df[df["Recession"] == 1].index
    if not recessions.empty:
        starts = [recessions[0]]
        ends = []
        for i in range(1, len(recessions)):
            # Gap >1 month ⇒ new recession block
            if (recessions[i] - recessions[i - 1]).days > 31:
                ends.append(recessions[i - 1])
                starts.append(recessions[i])
        ends.append(recessions[-1])

        for start, end in zip(starts, ends):
            fig.add_vrect(
                x0=start, x1=end,
                fillcolor="gray", opacity=0.2, line_width=0
            )

    # --- Display plot --- #
    st.plotly_chart(fig, use_container_width=True)

# ---------- Stand-alone run ---------- #
if __name__ == "__main__":
    render()
