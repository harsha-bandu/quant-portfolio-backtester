import pandas as pd
from universe.nifty50 import NIFTY50
from strategies.screener import run_screener
from datetime import datetime



# Run screener
final_df = run_screener(NIFTY50)


print("\nFinal Screened Stocks:\n")
print(final_df)

print("\nTop 5 Opportunities:\n")

print(
    final_df[
        [
            "Stock",
            "Score",
            "Category",
            "RSI",
            "ROE",
            "Revenue Growth %"
        ]
    ].head(5)
)

# Create timestamp

timestamp = datetime.now().strftime("%Y-%m-%d")

file_name = f"output/screened_stocks_{timestamp}.xlsx"

# Export Excel

final_df.to_excel(
    file_name,
    index=False
)

print(f"\nExcel exported: {file_name}")

print("\nExcel exported successfully.")