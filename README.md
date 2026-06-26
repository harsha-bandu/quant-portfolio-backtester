# 🚀 AlphaForge

> **A modular quantitative research framework for designing, testing, and evolving systematic investment strategies.**

AlphaForge is a Python-based quantitative research framework designed to help traders, investors, and researchers build systematic investment strategies using a clean, modular architecture.

Unlike traditional monolithic backtesting scripts, AlphaForge separates data processing, factor scoring, portfolio construction, analytics, and reporting into independent modules, making experimentation, testing, and future enhancements significantly easier.

---

# ✨ Current Features

## 📊 Research & Strategy

* Composite multi-factor stock scoring
* Trend Strength (200 DMA)
* Relative Strength Momentum
* RSI Momentum
* Volatility-adjusted scoring
* Monthly portfolio rebalancing

## 📈 Portfolio Management

* Top-N portfolio selection
* Holding persistence using ENTRY / EXIT ranks
* Sector diversification constraints
* Dynamic exposure scaling using market breadth
* Risk-adjusted position sizing
* Transaction cost modelling

## 📉 Performance Analytics

* CAGR
* Sharpe Ratio
* Volatility
* Maximum Drawdown
* Monthly return table
* Trade analytics
* Holdings history
* Score effectiveness analysis
* Benchmark comparison against NIFTY

## 🏗 Engineering

* Modular architecture
* Configuration-driven design
* Research snapshots
* Professional project structure
* Testing framework
* Extensible workflow engine

---

# 🧠 Strategy Overview

## 🌐 Universe

* NIFTY50 Stocks

## 📌 Stock Selection

Each month, stocks are ranked using a composite factor score based on:

* Trend Strength (Distance above 200 DMA)
* Relative Strength Momentum
* RSI
* Volatility Penalty

The highest-ranked stocks are considered for portfolio inclusion.

---

## 🏗 Portfolio Construction

* Monthly rebalancing
* Top 5 ranked stocks
* Holding persistence using ENTRY_RANK and EXIT_RANK
* Sector diversification limits
* Volatility-adjusted position sizing
* Maximum position weight constraints

---

## 🛡 Risk Management

Current risk controls include:

* Dynamic market exposure scaling
* Market breadth analysis
* Transaction costs
* Position weight limits
* Sector concentration limits

---

# 📊 Current Performance (Baseline v1.0.0)

| Metric                   |           Value |
| ------------------------ | --------------: |
| CAGR                     |      **10.57%** |
| Sharpe Ratio             |        **0.37** |
| Volatility               |      **13.63%** |
| Max Drawdown             |     **-22.59%** |
| Average Monthly Return   |       **0.92%** |
| Win Rate                 |      **50.00%** |
| Average Turnover         |      **93.88%** |
| Average Holding Duration | **2.05 Months** |

---

# 🏛 Architecture

```text
                    Workflow Engine
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
 Portfolio         Portfolio          Reporting
   Scoring        Construction        & Export
        │
        ▼
 Future Modules
 ├── Portfolio Simulation
 ├── Portfolio Metrics
 ├── Market Data Loader
 ├── Portfolio Optimizer
 ├── Walk Forward Analysis
 └── Machine Learning
```

---

# 📂 Project Structure

```text
AlphaForge/
│
├── analytics/
├── docs/
├── indicators/
├── reporting/
├── research/
│   ├── experiments/
│   └── snapshots/
├── strategies/
├── tests/
├── universe/
│
├── config.py
├── requirements.txt
├── run_portfolio_backtest.py
└── README.md
```

---

# ⚙ Installation

```bash
git clone https://github.com/<harsha-bandu>/AlphaForge.git

cd AlphaForge

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt
```

---

# ▶ Quick Start

Run the portfolio backtest:

```bash
python run_portfolio_backtest.py
```

Run the stock screener:

```bash
python main.py
```

---

# 🛣 Roadmap

## ✅ Version 1.x

* Modular project architecture
* Composite factor scoring
* Portfolio construction engine
* Dynamic market exposure
* Reporting framework
* Testing infrastructure

## 🚧 Version 2.x

* Portfolio simulation module
* Portfolio metrics module
* Market data loader
* Walk-forward optimization
* Portfolio optimization

## 🔬 Version 3.x

* Machine learning ranking
* Factor attribution
* Regime detection
* Advanced research framework

## 🤖 Version 4.x

* AI-assisted research
* Automated strategy comparison
* Intelligent reporting
* Research agents

---

# 📚 Documentation

Detailed documentation is available in the `docs/` directory.

* Architecture
* Engineering Principles
* Manifesto
* Roadmap

---

# 🛠 Tech Stack

* Python
* Pandas
* NumPy
* Matplotlib
* yFinance

---

# 🤝 Contributing

AlphaForge is an evolving quantitative research platform.

Contributions, discussions, feature suggestions, and research ideas are welcome.

---

# ⚠ Disclaimer

This project is intended for educational and research purposes only.

It does **not** constitute financial or investment advice. Always perform your own due diligence before making investment decisions.

---

# 📄 License

This project is licensed under the MIT License.
