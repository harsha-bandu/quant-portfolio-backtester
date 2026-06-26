import matplotlib.pyplot as plt
import pandas as pd
from reporting.excel_exporter import export_results
from strategies.portfolio_backtest import (
    run_portfolio_backtest
)

results = run_portfolio_backtest()

trade_logs = results["Trade Logs"]
monthly_returns = results["Monthly Returns"]

holdings_history = results["Holdings History"]

exported_files = export_results(results)

monthly_returns["Year"] = (pd.to_datetime(monthly_returns["Month"]).dt.year)

monthly_returns["Month Name"] = (pd.to_datetime(monthly_returns["Month"]).dt.strftime("%b"))

month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

monthly_pivot = monthly_returns.pivot(index="Year", columns="Month Name", values="Return %")

monthly_pivot = monthly_pivot.reindex(columns=month_order)

print("\nMonthly Return Table:\n")

print(monthly_pivot.round(2))

print("\nTrade Analytics:\n")
top_winners = (trade_logs.sort_values("Trade Return %", ascending=False).head(10))

print("\nTop Winning Trades:\n")
print(top_winners[["Month", "Stock", "Trade Return %", "Score"]])

top_losers = (trade_logs.sort_values("Trade Return %", ascending=True).head(10))

print("\nTop Losing Trades:\n")
print(top_losers[["Month", "Stock", "Trade Return %", "Score"]])

stock_summary = (trade_logs.groupby("Stock").agg({"Trade Return %": ["mean", "count"]}))
stock_summary.columns = ["Avg Return %", "Trades"]
stock_summary = (stock_summary.sort_values("Avg Return %", ascending=False))

print("\nBest Performing Stocks:\n")
print(stock_summary.head(10))

trade_logs["Score Bucket"] = pd.cut(trade_logs["Score"], bins=[0, 20, 40, 60, 80, 100, 120],
                                    labels=["0-20", "20-40", "40-60", "60-80", "80-100", "100-120"])

score_analysis = (trade_logs.groupby("Score Bucket", observed=False)["Trade Return %"].mean())

print("\nScore Effectiveness:\n")
print(score_analysis)

trade_logs.to_excel("output/trade_logs.xlsx", index=False)

print("\nPortfolio Backtest Results:\n")

for key, value in results.items():

    if key not in [
        "Equity Curve",
        "Benchmark Curve",
        "Timeline",
        "Zero Exposure Months",
        "Trade Logs",
        "Monthly Returns"
    ]:

        print(f"{key}: {value}")

equity_curve = results["Equity Curve"]

benchmark_curve = results["Benchmark Curve"]

timeline = results["Timeline"]

cash_months = results["Zero Exposure Months"]

plt.figure(figsize=(14, 7))

# =========================
# MAIN LINES
# =========================

plt.plot(
    timeline,
    equity_curve,
    label="Strategy"
)

plt.plot(
    timeline,
    benchmark_curve,
    label="NIFTY"
)

# =========================
# CASH MARKERS
# =========================

cash_x = []
cash_y = []

for i in range(len(cash_months)):

    if cash_months[i]:

        cash_x.append(timeline[i])
        cash_y.append(equity_curve[i])

plt.scatter(cash_x, cash_y, marker="o", s=120, label="Zero Exposure")

# =========================
# FORMATTING
# =========================

plt.title("Strategy vs NIFTY")
plt.xlabel("Timeline")
plt.ylabel("Portfolio Value")
#plt.xticks(timeline[::3], fontsize=8)
tick_positions = range(0, len(timeline), 1)
tick_labels = [timeline[i][:7] for i in tick_positions]
plt.xticks(tick_positions, tick_labels, fontsize=6, rotation=90)
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

plt.figure(figsize=(8, 5))

plt.scatter(trade_logs["Score"], trade_logs["Trade Return %"])
plt.title("Score vs Trade Return")
plt.xlabel("Score")
plt.ylabel("Trade Return %")
plt.grid(True)
plt.show()