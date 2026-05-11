import streamlit as st
import pandas as pd

from strategies.screener import run_screener
from universe.nifty50 import NIFTY50
from analytics.visuals import create_stock_chart


# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="NSE Stock Screener",
    layout="wide"
)

st.title("📈 NSE Stock Screener")

st.write(
    "Hybrid Fundamental + Technical Ranking System"
)


# =========================
# SESSION STATE
# =========================

if "final_df" not in st.session_state:
    st.session_state.final_df = None


# =========================
# RUN SCREENER BUTTON
# =========================

if st.button("Run Screener"):

    with st.spinner("Scanning NIFTY50 stocks..."):

        st.session_state.final_df = run_screener(
            NIFTY50
        )

    st.success("Screening Completed!")


# =========================
# LOAD RESULTS
# =========================

final_df = st.session_state.final_df


# =========================
# SHOW RESULTS
# =========================

if final_df is not None:

    # =========================
    # CATEGORY FILTER
    # =========================

    all_categories = [
        "Elite",
        "Strong",
        "Balanced",
        "Watchlist"
    ]

    categories = st.multiselect(
        "Filter Categories",
        options=all_categories,
        default=all_categories
    )

    filtered_df = final_df[
        final_df["Category"].isin(categories)
    ]


    # =========================
    # TOP PICKS
    # =========================

    st.subheader("🏆 Top Opportunities")

    st.dataframe(
        filtered_df.head(10),
        width='stretch'
    )


    # =========================
    # FULL RESULTS
    # =========================

    st.subheader("📊 Full Results")

    st.dataframe(
        filtered_df,
        width='stretch'
    )


    # =========================
    # STOCK CHART
    # =========================

    st.subheader("📈 Stock Chart")

    selected_stock = st.selectbox(
        "Select a stock to visualize",
        filtered_df["Stock"]
    )

    chart = create_stock_chart(
        selected_stock
    )

    if chart:
        st.plotly_chart(
            chart,
            width='stretch'
        )


    # =========================
    # DOWNLOAD BUTTON
    # =========================

    csv = filtered_df.to_csv(index=False)

    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="screened_stocks.csv",
        mime="text/csv"
    )