import yfinance as yf
import pandas as pd
import numpy as np

from universe.nifty50 import NIFTY50
from indicators.indicators import calculate_indicators
from config import *


# =====================================================
# STOCK SCORING FUNCTION
# =====================================================

def get_stock_score(df, date):

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
    # RSI SCORE
    # =====================================================

    rsi_score = (
        (rsi - 40)
        / 40
    ) * RSI_WEIGHT

    # =====================================================
    # TREND SCORE
    # =====================================================

    trend_score = (
        np.log1p(
            max(trend_strength, 0)
        )
    ) * TREND_WEIGHT

    # =====================================================
    # RELATIVE STRENGTH SCORE
    # =====================================================

    relative_strength_score = (
        np.log1p(
            max(six_month_return, 0)
        )
    ) * RELATIVE_STRENGTH_WEIGHT

    # =====================================================
    # VOLATILITY PENALTY
    # =====================================================

    volatility_penalty = (
        volatility * 100 * VOLATILITY_PENALTY_WEIGHT
    )

    # =====================================================
    # FINAL SCORE
    # =====================================================

    score = (
        rsi_score
        + trend_score
        + relative_strength_score
        - volatility_penalty
    )

    score = max(score, 0)

    return score


# =====================================================
# MAIN BACKTEST
# =====================================================

def run_portfolio_backtest():

    stock_data = {}

    # =====================================================
    # NIFTY BENCHMARK
    # =====================================================

    nifty_df = yf.download(
        "^NSEI",
        #period="5y",
        period=f"{BACKTEST_YEARS}y",
        interval="1d",
        progress=False
    )

    nifty_df.columns = nifty_df.columns.get_level_values(0)

    nifty_df = calculate_indicators(nifty_df)

    # =====================================================
    # DOWNLOAD STOCK DATA
    # =====================================================

    for symbol in NIFTY50:

        print(f"Downloading {symbol}...")

        try:

            df = yf.download(
                symbol,
                #period="5y",
                period=f"{BACKTEST_YEARS}y",
                interval="1d",
                progress=False
            )

            if df.empty:
                continue

            df.columns = df.columns.get_level_values(0)

            df = calculate_indicators(df)

            stock_data[symbol] = df

        except Exception as e:

            print(f"Error downloading {symbol}: {e}")

            continue

    # =====================================================
    # PORTFOLIO VARIABLES
    # =====================================================

    portfolio_returns = []
    monthly_return_table = []

    #equity_curve = [100]
    equity_curve = [STARTING_CAPITAL]

    #benchmark_curve = [100]
    benchmark_curve = [STARTING_CAPITAL]

    trade_logs = []

    timeline = ["Start"]

    cash_months = [False]

    current_holdings = []

    # =====================================================
    # DATE PREPARATION
    # =====================================================

    dates = stock_data[
        list(stock_data.keys())[0]
    ].index

    date_df = pd.DataFrame(index=dates)

    date_df['Month'] = (
        date_df.index.to_period('M')
    )

    month_end_indexes = (
        date_df
        .groupby('Month')
        .tail(1)
        .index
    )

    # =====================================================
    # MONTHLY REBALANCING
    # =====================================================

    for j in range(
        10,
        len(month_end_indexes) - 1
    ):

        current_date = month_end_indexes[j]

        next_date = month_end_indexes[j + 1]

        current_month_label = (
            current_date.strftime("%Y-%m-%d")
        )

        # =====================================================
        # MARKET REGIME FILTER
        # =====================================================

        nifty_price = (
            nifty_df
            .loc[current_date]['Close']
        )

        nifty_dma = (
            nifty_df
            .loc[current_date]['DMA_200']
        )

        # =====================================================
        # BENCHMARK ALWAYS MOVES
        # =====================================================

        nifty_entry = (
            nifty_df
            .loc[current_date]['Close']
        )

        nifty_exit = (
            nifty_df
            .loc[next_date]['Close']
        )

        nifty_return = (
            (nifty_exit - nifty_entry)
            / nifty_entry
        ) * 100

        new_benchmark = (
            benchmark_curve[-1]
            * (1 + nifty_return / 100)
        )

        benchmark_curve.append(
            new_benchmark
        )

        # =====================================================
        # CASH REGIME
        # =====================================================

        if nifty_price < nifty_dma:

            portfolio_returns.append(0)

            equity_curve.append(
                equity_curve[-1]
            )

            timeline.append(
                current_month_label
            )

            cash_months.append(True)

            continue

        # =====================================================
        # SCORE STOCKS
        # =====================================================

        monthly_scores = []

        for symbol, df in stock_data.items():

            if (
                current_date not in df.index
                or next_date not in df.index
            ):
                continue

            score = get_stock_score(
                df,
                current_date
            )

            if score is not None:

                monthly_scores.append({

                    "Symbol": symbol,

                    "Score": score
                })

        # =====================================================
        # NO VALID STOCKS
        # =====================================================

        if len(monthly_scores) == 0:

            portfolio_returns.append(0)

            equity_curve.append(
                equity_curve[-1]
            )

            timeline.append(
                current_month_label
            )

            cash_months.append(True)

            continue

        # =====================================================
        # TOP 5 STOCKS
        # =====================================================

        # top_stocks = sorted(
        #     monthly_scores,
        #     key=lambda x: x["Score"],
        #     reverse=True
        # )[:TOP_STOCKS]

        ranked_stocks = sorted(
            monthly_scores,
            key=lambda x: x["Score"],
            reverse=True
        )

        top_symbols = [
            x["Symbol"]
            for x in ranked_stocks[:HOLD_THRESHOLD_RANK]
        ]

        new_holdings = []

        # ==================================
        # KEEP EXISTING WINNERS
        # ==================================

        for stock in ranked_stocks:

            symbol = stock["Symbol"]

            if (
                symbol in current_holdings
                and symbol in top_symbols
            ):

                new_holdings.append(stock)

        # ==================================
        # ADD NEW STRONG STOCKS
        # ==================================

        for stock in ranked_stocks:

            if len(new_holdings) >= TOP_STOCKS:
                break

            if stock not in new_holdings:

                new_holdings.append(stock)

        top_stocks = new_holdings[:TOP_STOCKS]

        current_holdings = [
            x["Symbol"]
            for x in top_stocks
        ]

        # =====================================================
        # HOLDING RETURNS
        # =====================================================

        weighted_returns = []

        for stock in top_stocks:

            symbol = stock["Symbol"]

            df = stock_data[symbol]

            # ==================================
            # ENTRY PRICE
            # ==================================

            entry_price = (
                df.loc[current_date]['Close']
            )

            # ==================================
            # HOLDING PERIOD
            # ==================================

            holding_period = df.loc[
                current_date:next_date
            ]

            # ==================================
            # DEFAULT EXIT = MONTH END
            # ==================================

            exit_price = (
                holding_period.iloc[-1]['Close']
            )

            stop_loss_triggered = False

            # ==================================
            # 10% STOP LOSS
            # ==================================

            for k in range(len(holding_period)):

                current_close = (
                    holding_period.iloc[k]['Close']
                )

                drawdown = (
                    (current_close - entry_price)
                    / entry_price
                ) * 100

                if drawdown <= -STOP_LOSS_PCT:

                    exit_price = current_close

                    stop_loss_triggered = True

                    break

            # ==================================
            # ATR STOP LOSS
            # ==================================

            # atr = df.loc[current_date]['ATR']

            # atr_stop_pct = (
            #     (atr / entry_price)
            #     * 100
            #     * ATR_STOP_MULTIPLIER
            # )

            # for k in range(len(holding_period)):

            #     current_close = (
            #         holding_period.iloc[k]['Close']
            #     )

            #     drawdown = (
            #         (current_close - entry_price)
            #         / entry_price
            #     ) * 100

            #     if drawdown <= -atr_stop_pct:

            #         exit_price = current_close

            #         stop_loss_triggered = True

            #         break

            # ==================================
            # FINAL RETURN
            # ==================================

            # return_pct = (
            #     (exit_price - entry_price)
            #     / entry_price
            # ) * 100
            gross_return_pct = (
                (exit_price - entry_price)
                / entry_price
            ) * 100

            return_pct = (
                gross_return_pct
                - TRANSACTION_COST_PCT
            )   

            # ==================================
            # VOLATILITY
            # ==================================

            volatility = (
                df.loc[current_date]['Volatility']
            )

            # ==================================
            # STORE RETURNS
            # ==================================

            weighted_returns.append({

                "Return": return_pct,

                "Score": stock["Score"],

                "Volatility": volatility
            })

            # ==================================
            # TRADE LOG
            # ==================================

            trade_logs.append({

                "Month": current_month_label,

                "Stock": symbol,

                "Entry Price": round(
                    float(entry_price),
                    2
                ),

                "Exit Price": round(
                    float(exit_price),
                    2
                ),

                "Trade Return %": round(
                    float(return_pct),
                    2
                ),

                "Score": round(
                    float(stock["Score"]),
                    2
                ),

                "Gross Return %": round(float(gross_return_pct), 2),

                "Net Return %": round(float(return_pct), 2),                                      

                "Stop Loss Hit": stop_loss_triggered
            })

        # =====================================================
        # RISK-ADJUSTED POSITION SIZING
        # =====================================================

        risk_adjusted_scores = []

        for item in weighted_returns:

            adjusted_score = (
                item["Score"]
                / max(
                    item["Volatility"],
                    0.0001
                )
            )

            risk_adjusted_scores.append(
                adjusted_score
            )

        total_adjusted_score = sum(
            risk_adjusted_scores
        )

        portfolio_return = 0

        for idx, item in enumerate(
            weighted_returns
        ):

            weight = (
                risk_adjusted_scores[idx]
                / total_adjusted_score
            )

            # ==================================
            # MAX POSITION CAP
            # ==================================

            weight = min(weight, MAX_POSITION_WEIGHT)
            # TODO:
            # Re-normalize weights after max cap

            portfolio_return += (
                item["Return"]
                * weight
            )

        portfolio_returns.append(
            portfolio_return
        )

        monthly_return_table.append({
            "Month": current_month_label,
            "Return %": round(portfolio_return, 2)
        })

        # =====================================================
        # UPDATE EQUITY CURVE
        # =====================================================

        new_equity = (
            equity_curve[-1]
            * (1 + portfolio_return / 100)
        )

        equity_curve.append(
            new_equity
        )

        timeline.append(
            current_month_label
        )

        cash_months.append(False)

    # =====================================================
    # FINAL METRICS
    # =====================================================

    portfolio_returns = np.array(
        portfolio_returns
    )

    avg_return = np.mean(
        portfolio_returns
    )

    win_rate = (
        len(
            portfolio_returns[
                portfolio_returns > 0
            ]
        )
        / len(portfolio_returns)
    ) * 100

    cumulative_return = (
        np.prod(
            1 + portfolio_returns / 100
        ) - 1
    )

    # =====================================================
    # CAGR
    # =====================================================

    years = (
        len(portfolio_returns)
        / 12
    )

    cagr = (
        (
            equity_curve[-1]
            / equity_curve[0]
        ) ** (1 / years) - 1
    ) * 100

    # =====================================================
    # VOLATILITY
    # =====================================================

    volatility = (
        np.std(portfolio_returns)
        * np.sqrt(12)
    )

    # =====================================================
    # SHARPE RATIO
    # =====================================================

    #risk_free_rate = 6
    risk_free_rate = RISK_FREE_RATE

    sharpe_ratio = (
        (
            avg_return * 12
            - risk_free_rate
        )
        / volatility
    )

    # =====================================================
    # MAX DRAWDOWN
    # =====================================================

    equity_array = np.array(
        equity_curve
    )

    running_max = np.maximum.accumulate(
        equity_array
    )

    drawdowns = (
        equity_array
        - running_max
    ) / running_max

    max_drawdown = (
        np.min(drawdowns)
        * 100
    )

    # =====================================================
    # RETURN RESULTS
    # =====================================================

    return {

        "Average Monthly Return %": round(
            avg_return,
            2
        ),

        "Win Rate %": round(
            win_rate,
            2
        ),

        "Total Return %": round(
            cumulative_return * 100,
            2
        ),

        "Number of Months": len(
            portfolio_returns
        ),

        "CAGR %": round(
            cagr,
            2
        ),

        "Volatility %": round(
            volatility,
            2
        ),

        "Sharpe Ratio": round(
            sharpe_ratio,
            2
        ),

        "Max Drawdown %": round(
            max_drawdown,
            2
        ),

        "Equity Curve": equity_curve,

        "Benchmark Curve": benchmark_curve,

        "Timeline": timeline,

        "Cash Months": cash_months,

        "Trade Logs": pd.DataFrame(trade_logs),

        "Monthly Returns": pd.DataFrame(monthly_return_table)

    }

