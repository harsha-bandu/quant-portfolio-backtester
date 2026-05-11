import yfinance as yf
import pandas as pd
from fundamentals import get_fundamentals
from indicators.indicators import calculate_indicators
from concurrent.futures import ThreadPoolExecutor #commonly used in web scraping, API systems, quant tools, data pipelines

def process_stock(symbol):

    try:

        print(f"\nProcessing {symbol}...")

        # Download data
        df = yf.download(
            symbol,
            period="1y",
            interval="1d",
            progress=False
        )

        if df.empty:
            print(f"SKIPPED -> No data for {symbol}")
            return None

        # Indicators
        df = calculate_indicators(df)

        latest = df.iloc[-1]

        current_price = latest['Close'].item()
        dma_200 = latest['DMA_200'].item()
        rsi = latest['RSI'].item()

        current_volume = latest['Volume'].item()
        avg_volume = latest['AVG_VOLUME_20'].item()

        # Fundamentals
        fundamentals = get_fundamentals(symbol)

        pe_ratio = fundamentals["PE Ratio"]
        market_cap = fundamentals["Market Cap"]
        roe = fundamentals["ROE"]
        debt_equity = fundamentals["Debt/Equity"]
        revenue_growth = fundamentals["Revenue Growth"]

        # Core calculations
        above_dma = current_price > dma_200

        volume_ratio = current_volume / avg_volume

        trend_strength = (
            (current_price - dma_200)
            / dma_200
        ) * 100

        # =========================
        # FACTOR SCORING SYSTEM
        # =========================

        rsi_score = min(rsi, 70) / 70 * 20

        trend_score = (
            min(trend_strength, 20)
            / 20
            * 20
        )

        volume_score = (
            min(volume_ratio, 3)
            / 3
            * 15
        )

        if roe is not None:
            roe_score = (
                min(roe * 100, 25)
                / 25
                * 20
            )
        else:
            roe_score = 0

        if revenue_growth is not None:
            growth_score = (
                min(revenue_growth * 100, 20)
                / 20
                * 15
            )
        else:
            growth_score = 0

        if debt_equity is not None:

            if debt_equity < 50:
                debt_score = 10

            elif debt_equity < 100:
                debt_score = 5

            else:
                debt_score = 0

        else:
            debt_score = 0

        # Final Score

        score = (
            rsi_score +
            trend_score +
            volume_score +
            roe_score +
            growth_score +
            debt_score
        )

        # Categories

        if score >= 75:
            category = "Elite"

        elif score >= 60:
            category = "Strong"

        elif score >= 45:
            category = "Balanced"

        else:
            category = "Watchlist"

        # Final filter

        if above_dma:

            print(f"PASSED | Score: {round(score,2)}")

            return {
                "Stock": symbol,
                "Category": category,
                "Current Price": round(current_price, 2),
                "200 DMA": round(dma_200, 2),
                "RSI": round(rsi, 2),
                "Volume Ratio": round(volume_ratio, 2),
                "Trend Strength %": round(trend_strength, 2),
                "PE Ratio": round(pe_ratio, 2) if pe_ratio else None,
                "ROE": round(roe * 100, 2) if roe else None,
                "Debt/Equity": round(debt_equity, 2) if debt_equity else None,
                "Revenue Growth %": round(revenue_growth * 100, 2) if revenue_growth else None,
                "Score": round(score, 2)
            }

        else:

            print("FAILED -> Below 200 DMA")

            return None

    except Exception as e:

        print(f"Error in {symbol}: {e}")

        return None
    

def run_screener(symbols):

    results = []

    with ThreadPoolExecutor(max_workers=10) as executor:

        processed = executor.map(
            process_stock,
            symbols
        )

    for stock_result in processed:

        if stock_result is not None:
            results.append(stock_result)

    final_df = pd.DataFrame(results)

    # Custom category ranking

    category_order = {
        "Elite": 1,
        "Strong": 2,
        "Balanced": 3,
        "Watchlist": 4
    }

    final_df["Category Rank"] = (
        final_df["Category"]
        .map(category_order)
    )

    if not final_df.empty:

        final_df = final_df.sort_values(
                by=["Category Rank", "Score"],
                ascending=[True, False]
                )
        
        final_df = final_df.drop(columns=["Category Rank"])

    return final_df