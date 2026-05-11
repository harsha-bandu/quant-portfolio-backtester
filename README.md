# 📈 Quant Portfolio Backtester

A quantitative portfolio backtesting framework for momentum and trend-following strategies on NIFTY50 stocks using Python.

This project simulates monthly portfolio rebalancing using technical indicators, relative strength ranking, volatility-adjusted weighting, and market regime filtering.

---

# 🚀 Features

- 📅 Monthly portfolio rebalancing
- 📊 Momentum-based stock ranking
- 📈 RSI + Trend + Relative Strength scoring
- ⚖️ Volatility-adjusted portfolio weighting
- 🛡️ Market regime filter using NIFTY 200 DMA
- 🚨 Intra-month stop loss handling
- 📉 Benchmark comparison vs NIFTY
- 📌 Equity curve visualization
- 🧾 Trade-level analytics
- 🔍 Score effectiveness analysis
- 📐 Risk metrics and portfolio statistics

---

# 🧠 Strategy Logic

## 🌐 Universe
- NIFTY50 stocks

## 📌 Stock Selection

Stocks are ranked monthly using a composite score based on:

- RSI momentum
- Distance above 200 DMA
- Relative strength over lookback period
- Volatility penalty

## 🏗️ Portfolio Construction

- Top 5 ranked stocks selected monthly
- Volatility-adjusted position sizing
- Position weight caps applied

## 🛡️ Risk Management

- NIFTY 200 DMA regime filter
- Move to cash during weak market conditions
- 10% intra-month stop loss

## 🔄 Rebalancing

- Monthly

---

# 📊 Backtest Metrics

| Metric | Value |
|---|---|
| CAGR | ~14% - 17% |
| Sharpe Ratio | ~0.5 - 0.7 |
| Max Drawdown | ~18% - 20% |
| Win Rate | ~46% - 52% |
| Test Window | 5 Years |

---

# 🖼️ Example Outputs

## 📈 Strategy vs NIFTY

![Equity Curve](output/charts/strategy_vs_nifty.png)

## 🔍 Score vs Trade Return

![Scatter Plot](output/charts/score_vs_trade.png)

---

# 🗂️ Project Structure

```text
analytics/
indicators/
strategies/
universe/
output/
```

---

# ⚙️ Installation

```bash
git clone https://github.com/harsha-bandu/quant-portfolio-backtester.git
```

```bash
pip install -r requirements.txt
```

---

# ▶️ Run Backtest

```bash
python run_portfolio_backtest.py
```

---

# 🧪 Current Enhancements

Implemented:

- Relative strength scoring
- Volatility-adjusted weighting
- Dynamic position sizing
- Intra-month stop loss handling
- Risk-adjusted portfolio allocation
- Score effectiveness analytics
- Trade-level analytics

---

# 🔮 Planned Improvements

- ATR-based stop loss
- Sector exposure caps
- Transaction cost simulation
- Walk-forward testing
- Hyperparameter optimization
- Factor attribution analysis
- Market breadth indicators
- Multi-factor ranking engine

---

# 🛠️ Tech Stack

- Python
- Pandas
- NumPy
- Matplotlib
- yFinance

---

# ⚠️ Disclaimer

This project is for educational and research purposes only and does not constitute financial advice.
