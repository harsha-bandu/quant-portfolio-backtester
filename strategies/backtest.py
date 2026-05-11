import yfinance as yf
import pandas as pd

from indicators.indicators import calculate_indicators


def backtest_stock(symbol):

    try:

        # Download historical data
        df = yf.download(
            symbol,
            period="3y",
            interval="1d",
            progress=False
        )

        if df.empty:
            return None

        # Flatten columns
        df.columns = df.columns.get_level_values(0)

        # Indicators
        df = calculate_indicators(df)

        trades = []

        # Start after enough data
        for i in range(220, len(df) - 20):

            row = df.iloc[i]

            current_price = row['Close']
            dma_200 = row['DMA_200']
            rsi = row['RSI']

            # Basic strategy
            if (
                current_price > dma_200 and
                50 <= rsi <= 70
            ):

                entry_price = current_price

                exit_price = df.iloc[i + 20]['Close']

                return_pct = (
                    (exit_price - entry_price)
                    / entry_price
                ) * 100

                trades.append(return_pct)

        if len(trades) == 0:
            return None

        # Metrics
        avg_return = sum(trades) / len(trades)

        win_rate = (
            len([x for x in trades if x > 0])
            / len(trades)
        ) * 100

        return {

            "Stock": symbol,
            "Trades": len(trades),
            "Average Return %": round(avg_return, 2),
            "Win Rate %": round(win_rate, 2)

        }

    except Exception as e:

        print(f"Backtest error for {symbol}: {e}")

        return None