import streamlit as st
import time
import plotly.graph_objects as go

from websocket_client import start_socket, latest_ticks
from storage import save_tick, load_data
from analytics import compute_analytics


# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Crypto Analytics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Real-Time Crypto Statistical Analytics")
st.caption("Live Binance WebSocket • Statistical Arbitrage Helper Dashboard")


# ---------- SIDEBAR ----------
st.sidebar.header("⚙ Controls")

symbols = ["btcusdt", "ethusdt", "bnbusdt", "adausdt", "xrpusdt"]

symbol1 = st.sidebar.selectbox("Symbol 1", symbols, index=0)
symbol2 = st.sidebar.selectbox("Symbol 2", symbols, index=1)

window = st.sidebar.slider("Rolling Window", 10, 50, 20)
z_alert = st.sidebar.slider("Z-Score Alert Threshold", 1.0, 3.0, 2.0)

st.sidebar.markdown("---")
st.sidebar.info(
    "📌 Analytics:\n"
    "- OLS Hedge Ratio\n"
    "- Spread & Z-Score\n"
    "- Rolling Correlation\n"
    "- Live Alerts"
)


# ---------- START SOCKETS ----------
start_socket(symbol1)
start_socket(symbol2)

placeholder = st.empty()


# ---------- MAIN LOOP ----------
while True:
    if latest_ticks:
        for tick in latest_ticks[-5:]:
            save_tick(tick["symbol"].lower(), tick)

        df1 = load_data(symbol1).dropna()
        df2 = load_data(symbol2).dropna()

        if len(df1) > window and len(df2) > window:
            analytics_df, hedge_ratio = compute_analytics(df1, df2, window)

            with placeholder.container():

                # ----- SUMMARY -----
                st.subheader("📋 Summary Statistics")

                c1, c2, c3 = st.columns(3)
                c1.metric("📐 Hedge Ratio", round(hedge_ratio, 3))
                c2.metric("📊 Latest Z-Score", round(analytics_df["zscore"].iloc[-1], 2))
                c3.metric("🔁 Correlation", round(analytics_df["correlation"].iloc[-1], 2))

                if abs(analytics_df["zscore"].iloc[-1]) > z_alert:
                    st.warning(
                        f"🚨 Z-Score Alert Triggered: {analytics_df['zscore'].iloc[-1]:.2f}"
                    )

                st.markdown("---")

                # ----- PRICE CHART -----
                st.subheader("📈 Price Comparison")

                fig_price = go.Figure()
                fig_price.add_trace(go.Scatter(
                    x=analytics_df.index,
                    y=analytics_df["price1"],
                    mode="lines",
                    name=symbol1.upper(),
                    yaxis="y1"
                ))
                fig_price.add_trace(go.Scatter(
                    x=analytics_df.index,
                    y=analytics_df["price2"],
                    mode="lines",
                    name=symbol2.upper(),
                    yaxis="y2"
                ))
                fig_price.update_layout(
                    height=350,
                    template="plotly_dark",
                    xaxis_title="Time",
                    yaxis=dict(title=symbol1.upper(), side="left"),
                    yaxis2=dict(title=symbol2.upper(), overlaying="y", side="right")
                )
                st.plotly_chart(fig_price, use_container_width=True)

                # ----- SPREAD & Z-SCORE -----
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("📉 Spread")
                    fig_spread = go.Figure()
                    fig_spread.add_trace(go.Scatter(
                        x=analytics_df.index,
                        y=analytics_df["spread"],
                        mode="lines"
                    ))
                    fig_spread.update_layout(height=300, template="plotly_dark")
                    st.plotly_chart(fig_spread, use_container_width=True)

                with col2:
                    st.subheader("📊 Z-Score")
                    fig_z = go.Figure()
                    fig_z.add_trace(go.Scatter(
                        x=analytics_df.index,
                        y=analytics_df["zscore"],
                        mode="lines"
                    ))
                    fig_z.add_hline(y=z_alert, line_dash="dash", line_color="red")
                    fig_z.add_hline(y=-z_alert, line_dash="dash", line_color="red")
                    fig_z.update_layout(height=300, template="plotly_dark")
                    st.plotly_chart(fig_z, use_container_width=True)

                # ----- CORRELATION -----
                st.subheader("🔁 Rolling Correlation")
                fig_corr = go.Figure()
                fig_corr.add_trace(go.Scatter(
                    x=analytics_df.index,
                    y=analytics_df["correlation"],
                    mode="lines"
                ))
                fig_corr.update_layout(height=300, template="plotly_dark")
                st.plotly_chart(fig_corr, use_container_width=True)

    time.sleep(2)  # refresh every 2 seconds