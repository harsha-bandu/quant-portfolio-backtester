import pandas as pd

from backtest import backtest_stock
from nifty50 import NIFTY50


results = []

for symbol in NIFTY50:

    print(f"Testing {symbol}...")

    result = backtest_stock(symbol)

    if result:
        results.append(result)


final_df = pd.DataFrame(results)

final_df = final_df.sort_values(
    by="Average Return %",
    ascending=False
)

print("\nBacktest Results:\n")

print(final_df)