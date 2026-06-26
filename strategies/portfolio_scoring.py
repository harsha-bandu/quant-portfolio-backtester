"""
Portfolio Scoring Engine

Responsible for:
- Factor extraction
- Factor normalization
- Composite score calculation
- Universe ranking

This module contains no portfolio construction or trade simulation logic.
"""

import pandas as pd
from config import (
    RSI_WEIGHT,
    TREND_WEIGHT,
    RELATIVE_STRENGTH_WEIGHT,
    VOLATILITY_PENALTY_WEIGHT,
    RELATIVE_STRENGTH_LOOKBACK,
)

# =====================================================
# STOCK SCORING FUNCTION
# =====================================================

def extract_stock_factors(df, date):
    """
    Calculate scoring factors for a stock at a given date.
    
    Args:
        df: DataFrame with OHLCV and calculated indicators
        date: The date to score the stock
        
    Returns:
        Dictionary with factor values (Trend, RSI, Momentum, Volatility)
        or None if stock doesn't meet criteria or has missing data
    """

    if date not in df.index:
        return None

    row = df.loc[date]

    current_price = row['Close']
    dma_200 = row['DMA_200']
    rsi = row['RSI']
    volatility = row['Volatility']

    if (
        pd.isna(dma_200)
        or pd.isna(rsi)
        or pd.isna(volatility)
    ):
        return None

    # =====================================================
    # ONLY STOCKS ABOVE 200 DMA
    # =====================================================

    if current_price < dma_200:
        return None

    # =====================================================
    # TREND STRENGTH
    # =====================================================

    trend_strength = (
        (current_price - dma_200)
        / dma_200
    ) * 100

    # =====================================================
    # RELATIVE STRENGTH
    # =====================================================

    past_price = (
        df.shift(RELATIVE_STRENGTH_LOOKBACK)
        .loc[date]['Close']
    )

    if pd.isna(past_price):
        return None

    six_month_return = (
        (current_price - past_price)
        / past_price
    ) * 100

    # =====================================================
    # RETURN FACTORS
    # =====================================================

    return {
        "Trend": trend_strength,
        "RSI": rsi,
        "Momentum": six_month_return,
        "Volatility": volatility
    }


# =====================================================
# SCORE UNIVERSE
# =====================================================

def score_universe(stock_data, current_date):
    """
    Score all stocks in the universe for a given date.
    
    Args:
        stock_data: Dictionary with stock symbols as keys and 
                   DataFrames with indicators as values
        current_date: The date to score all stocks
        
    Returns:
        List of dictionaries with stock scores and factors,
        ranked by composite score (highest first).
        Each dict contains: Symbol, Score, Trend, RSI, Momentum, Volatility,
        and percentile ranks (Trend Rank, RSI Rank, Momentum Rank, Volatility Rank)
    """

    # =====================================================
    # COLLECT STOCK FACTORS
    # =====================================================

    monthly_scores = []

    for symbol, df in stock_data.items():

        if current_date not in df.index:
            continue

        factors = extract_stock_factors(df, current_date)

        if factors is not None:
            monthly_scores.append({
                "Symbol": symbol,
                "Trend": factors["Trend"],
                "RSI": factors["RSI"],
                "Momentum": factors["Momentum"],
                "Volatility": factors["Volatility"]
            })

    # =====================================================
    # NO VALID STOCKS
    # =====================================================

    if len(monthly_scores) == 0:
        return []

    # =====================================================
    # FACTOR NORMALIZATION
    # =====================================================

    factor_df = pd.DataFrame(monthly_scores)

    factor_df["Trend Rank"] = (factor_df["Trend"].rank(pct=True))

    factor_df["RSI Rank"] = (factor_df["RSI"].rank(pct=True))

    factor_df["Momentum Rank"] = (factor_df["Momentum"].rank(pct=True))

    # Lower volatility preferred

    factor_df["Volatility Rank"] = (1 - factor_df["Volatility"].rank(pct=True))

    # =====================================================
    # COMPOSITE SCORE
    # =====================================================

    factor_df["Score"] = (
        factor_df["Trend Rank"] * TREND_WEIGHT
        + factor_df["RSI Rank"] * RSI_WEIGHT
        + factor_df["Momentum Rank"] * RELATIVE_STRENGTH_WEIGHT
        + factor_df["Volatility Rank"] * VOLATILITY_PENALTY_WEIGHT
    )

    # =====================================================
    # CONVERT BACK TO RECORDS
    # =====================================================

    monthly_scores = factor_df.to_dict("records")

    # =====================================================
    # FINAL RANKING
    # =====================================================

    ranked_stocks = sorted(monthly_scores, key=lambda x: x["Score"], reverse=True)

    return ranked_stocks
