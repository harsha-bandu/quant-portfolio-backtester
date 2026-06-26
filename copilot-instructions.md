# AlphaForge Copilot Instructions

> GitHub Copilot guidance for maintaining AlphaForge's modular, reproducible quantitative research architecture

---

## 📋 Table of Contents

1. [Project Architecture](#project-architecture)
2. [Module Design Principles](#module-design-principles)
3. [Workflow Engine Responsibilities](#workflow-engine-responsibilities)
4. [Configuration Management](#configuration-management)
5. [Testing & Validation](#testing--validation)
6. [Documentation Standards](#documentation-standards)
7. [Refactoring Philosophy](#refactoring-philosophy)
8. [Git Workflow](#git-workflow)
9. [Python Style Guide](#python-style-guide)

---

## Project Architecture

### Directory Structure

```
AlphaForge/
├── config.py                          # Global configuration & parameters
├── main.py                            # Entry point
├── fundamentals.py                    # Fundamental analysis utilities
├── run_backtest.py                    # Backtest execution script
├── run_portfolio_backtest.py          # Portfolio backtest runner
│
├── analytics/                         # Performance & attribution analysis
│   ├── attribution.py                 # Factor attribution analysis
│   ├── metrics.py                     # Risk & return metrics
│   └── visuals.py                     # Visualization utilities
│
├── app/                               # Streamlit/Web application
│   └── app.py                         # Dashboard & UI
│
├── core/                              # Core utilities
│   ├── constants.py                   # Project constants
│   ├── logger.py                      # Logging configuration
│   ├── metadata.py                    # Project metadata
│   └── version.py                     # Version tracking
│
├── data/                              # Data management
│   ├── cache/                         # Cached data (ignored in git)
│   └── raw/                           # Raw data sources
│
├── indicators/                        # Technical indicator library
│   └── indicators.py                  # TA calculations
│
├── output/                            # Analysis outputs
│   ├── charts/                        # Generated charts
│   ├── reports/                       # Analysis reports
│   └── trade_logs/                    # Trade execution records
│
├── reporting/                         # Report generation
│   ├── chart_generator.py             # Chart creation
│   ├── excel_exporter.py              # Excel export functionality
│   ├── html_report.py                 # HTML report generation
│   └── markdown_report.py             # Markdown report generation
│
├── research/                          # Research & experimentation
│   ├── baselines/                     # Baseline strategies
│   ├── experiments/                   # Experimental strategies
│   ├── reports/                       # Research reports
│   └── templates/                     # Report templates
│
├── screen/                            # Virtual environment
│   └── (Python venv - ignored in git)
│
├── strategies/                        # Strategy modules (core logic)
│   ├── backtest.py                    # Generic backtest engine
│   ├── portfolio_backtest.py          # Portfolio strategy backtest
│   ├── portfolio_scoring.py           # Stock scoring engine
│   ├── portfolio_construction.py      # Portfolio construction logic
│   ├── screener.py                    # Stock screening
│   └── docs/                          # Strategy documentation
│
└── universe/                          # Market universe definitions
    ├── nifty50.py                     # NIFTY50 constituent list
    ├── sector_map.py                  # Stock-to-sector mapping
    └── sectors.py                     # Sector definitions
```

### Architecture Layers

```
┌─────────────────────────────────────────────────┐
│  Presentation Layer (Dashboards, Reports)      │
│  app/, reporting/                              │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│  Analysis Layer (Analytics, Attribution)       │
│  analytics/                                     │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│  Strategy Execution Layer (Backtests)          │
│  strategies/: backtest.py,                      │
│  portfolio_backtest.py                         │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│  Portfolio Management Layer                    │
│  strategies/: portfolio_scoring.py,            │
│  portfolio_construction.py                     │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│  Data & Indicators Layer                       │
│  indicators/, universe/, data/                 │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│  Configuration & Core Utilities                │
│  config.py, core/                              │
└─────────────────────────────────────────────────┘
```

---

## Module Design Principles

### Single Responsibility

Each module owns one clear responsibility:

- **`portfolio_scoring.py`**: Factor extraction → normalization → composite scoring → ranking
- **`portfolio_construction.py`**: Rank filtering → holding persistence → sector constraints → turnover
- **`backtest.py`**: Trade simulation → P&L calculation → equity curve tracking
- **`indicators.py`**: Technical indicator calculations only
- **`analytics/*.py`**: Metrics, attribution, and visualization only

### Data Flow Contracts

When extracting functionality into new modules:

```python
# DO: Define clear input/output contracts
def score_universe(stock_data, current_date):
    """
    Args:
        stock_data: Dict[symbol, DataFrame]
        current_date: pd.Timestamp
    
    Returns:
        List[Dict] with keys: Symbol, Score, Trend, RSI, Momentum, Volatility
    """

# DON'T: Modify global state or return incompatible structures
def score_universe(stock_data):
    global ranked_stocks  # ❌ Never do this
    ranked_stocks = ...
    return  # ❌ Returns nothing, unclear contract
```

### Module Independence

- Modules should not import each other except through explicit dependencies
- Configuration comes exclusively from `config.py`
- Data structures are simple dicts and DataFrames (no custom classes unless necessary)
- Side effects limited to: writing files, updating passed-in containers

### Error Handling

```python
# DO: Return None/empty list for invalid states
def get_stock_score(df, date):
    if date not in df.index:
        return None  # Clear signal: data unavailable
    if missing_indicators:
        return None  # Clear signal: can't score

# DON'T: Raise exceptions for expected missing data
def get_stock_score(df, date):
    if date not in df.index:
        raise ValueError("Date not found")  # ❌ Breaks portfolio-level logic
```

---

## Workflow Engine Responsibilities

### Monthly Portfolio Backtest Flow

```
┌─────────────────────────────────────────────────────────┐
│ 1. Load Data & Calculate Indicators                     │
│    - yfinance download (NIFTY50 stocks + index)         │
│    - indicators.calculate_indicators(df)                 │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│ 2. Initialize Backtest Variables                        │
│    - equity_curve, portfolio_returns, trade_logs        │
│    - holding_durations, current_holdings               │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│ 3. FOR EACH MONTH:                                      │
│    a. Calculate market breadth (% stocks > 200 DMA)     │
│    b. Determine market exposure (0.0 to 1.0)           │
│    c. Score universe (portfolio_scoring.score_universe) │
│    d. Construct portfolio                              │
│       (portfolio_construction.construct_portfolio)      │
│    e. Simulate trades (stop losses, P&L)               │
│    f. Update equity curve & analytics                  │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│ 4. Calculate Final Metrics                              │
│    - CAGR, Sharpe, Max Drawdown, Win Rate              │
│    - Generate reports & visualizations                 │
└─────────────────────────────────────────────────────────┘
```

### Scoring Workflow (portfolio_scoring.py)

```
Input: stock_data dict, current_date
  ↓
FOR EACH SYMBOL:
  ├─ extract_stock_factors(df, date)
  │  ├─ Check price > 200 DMA (filter)
  │  ├─ Calculate trend_strength
  │  ├─ Calculate six_month_return
  │  └─ Return raw factor dict or None
  ├─ Collect valid factors into DataFrame
  ↓
Factor Normalization:
  ├─ Percentile rank all factors (0-1)
  ├─ Invert volatility rank (lower volatility = higher rank)
  ├─ Calculate weighted composite score
  ↓
Output: ranked_stocks list (sorted by score desc)
```

### Construction Workflow (portfolio_construction.py)

```
Input: ranked_stocks, current_holdings, holding_durations
  ↓
Build Rank Map:
  └─ Symbol → Rank (1-indexed, best first)
  ↓
Retain Holdings:
  ├─ Iterate ranked_stocks
  ├─ Keep if: symbol in current_holdings AND rank ≤ EXIT_RANK
  ↓
Add New Entries:
  ├─ Iterate ranked_stocks
  ├─ Add if: rank ≤ ENTRY_RANK AND not already selected
  ├─ Stop when portfolio_size == TOP_STOCKS
  ↓
Enforce Sector Constraints:
  ├─ Iterate selected stocks
  ├─ Filter out if sector count would exceed MAX_STOCKS_PER_SECTOR
  ├─ Stop when portfolio_size == TOP_STOCKS
  ↓
Track Holding Durations:
  ├─ Increment duration for continuing holds
  ├─ Record completion for exited stocks
  ├─ Calculate monthly turnover
  ↓
Output: top_stocks, new_current_holdings, updated holding_durations
```

---

## Configuration Management

### config.py Structure

All configurable parameters are centralized in `config.py`:

```python
# ==========================================
# BACKTEST SETTINGS
# ==========================================
BACKTEST_YEARS = 5           # Historical lookback
TOP_STOCKS = 5               # Portfolio size

# ==========================================
# SCORING PARAMETERS
# ==========================================
RSI_WEIGHT = 25              # Weight for RSI factor
TREND_WEIGHT = 12            # Weight for trend factor
RELATIVE_STRENGTH_WEIGHT = 4 # Weight for momentum factor
VOLATILITY_PENALTY_WEIGHT = 4# Weight for volatility (inverted)

# ==========================================
# RANKING & SELECTION
# ==========================================
ENTRY_RANK = 5               # Max rank to enter new position
EXIT_RANK = 12               # Max rank to retain existing position
MAX_STOCKS_PER_SECTOR = 2    # Sector diversification limit

# ==========================================
# RISK MANAGEMENT
# ==========================================
STOP_LOSS_PCT = 10           # Intra-month stop loss threshold
MAX_POSITION_WEIGHT = 0.30   # Max weight before normalization
RISK_FREE_RATE = 6           # For Sharpe ratio calculation

# ==========================================
# LOOKBACK WINDOWS
# ==========================================
RSI_WINDOW = 14              # RSI period
VOLATILITY_WINDOW = 20       # Volatility calculation period
RELATIVE_STRENGTH_LOOKBACK = 126  # 6-month lookback
```

### Parameter Changes

When modifying parameters:
1. **Always change `config.py` only** — never hardcode values in strategy modules
2. **Document the intent** — add a comment explaining the change
3. **Test impact** — run full backtest to verify expected behavior changes
4. **Version bump** — update PROJECT_METADATA.json if changing fundamentals

Example:
```python
# config.py
ENTRY_RANK = 5  # Changed from 8 (2025-06-15): tighter entry discipline
```

---

## Testing & Validation

### Behavior-Preserving Refactoring

When extracting or reorganizing code:

1. **Verify outputs are identical**:
   ```python
   # Before refactoring
   ranked_stocks_old = old_scoring_logic(stock_data, date)
   
   # After refactoring
   ranked_stocks_new = score_universe(stock_data, date)
   
   # Validate they're identical
   assert ranked_stocks_old == ranked_stocks_new
   ```

2. **Test with historical data**:
   - Run full backtest before and after refactoring
   - Compare: equity curves, Sharpe ratios, trade logs
   - Verify: no rounding errors, identical P&L

3. **Unit test new module functions**:
   ```python
   def test_score_universe_returns_ranked_list():
       ranked = score_universe(mock_stock_data, mock_date)
       assert isinstance(ranked, list)
       assert all('Score' in stock for stock in ranked)
       assert ranked == sorted(ranked, key=lambda x: x['Score'], reverse=True)
   
   def test_construct_portfolio_respects_rank_limits():
       result = construct_portfolio(ranked_stocks, [], {}, [], [])
       assert len(result['top_stocks']) <= TOP_STOCKS
   ```

### Regression Testing

Before committing strategy changes:

```bash
# Run full backtest, save metrics
python run_portfolio_backtest.py > backtest_v1.log

# Make changes
# ... edit strategy/config ...

# Run backtest again
python run_portfolio_backtest.py > backtest_v2.log

# Compare key metrics
diff backtest_v1.log backtest_v2.log
# If different: was it intentional? Document in commit message
```

---

## Documentation Standards

### Module Docstrings

Every module should start with a documentation block:

```python
"""
Portfolio Scoring Engine

Responsible for:
- Factor extraction and validation
- Factor normalization via percentile ranking
- Composite score calculation
- Universe ranking

This module contains no portfolio construction or trade simulation logic.
"""
```

### Function Docstrings

Use clear, actionable docstrings:

```python
def score_universe(stock_data, current_date):
    """
    Score all stocks in the universe for a given date.
    
    Args:
        stock_data: Dict[str, pd.DataFrame]
            Keys are stock symbols, values are DataFrames with
            OHLCV + calculated indicators (DMA_200, RSI, Volatility)
        current_date: pd.Timestamp
            The date to score all stocks
        
    Returns:
        List[Dict]
            List of scored stocks sorted by composite score (highest first).
            Each dict contains:
            - Symbol: str
            - Score: float (weighted composite score)
            - Trend: float (% above 200 DMA)
            - RSI: float (14-period RSI)
            - Momentum: float (6-month return %)
            - Volatility: float (20-day rolling volatility)
            - Trend Rank, RSI Rank, Momentum Rank, Volatility Rank: float (0-1)
    """
```

### Inline Comments

Comment the "why", not the "what":

```python
# ❌ DON'T: State the obvious
for symbol in stock_data:
    df = stock_data[symbol]  # Get DataFrame for symbol

# ✅ DO: Explain intent and assumptions
# Only include stocks where today's price is above 200-day MA
# (filters out weak trends and downtrends)
if current_price < dma_200:
    return None
```

### README Updates

When adding new modules or features:
1. Update `strategies/docs/roadmap.md` with completed/planned items
2. Add brief description in project README.md
3. Document any new configuration parameters

---

## Refactoring Philosophy

### When to Refactor

✅ **DO refactor when**:
- Module exceeds ~300 lines (violates SRP)
- Code is duplicated across 2+ places
- Extracting enables testability
- Module dependencies form a cycle
- Behavior is unclear despite comments

❌ **DON'T refactor when**:
- "Just because" (premature abstraction)
- Tests would take longer to write than the refactor
- Core algorithm logic is being changed (separate PR)

### Extraction Checklist

Before extracting code into a new module:

- [ ] Extracted function has clear, single responsibility
- [ ] All dependencies are passed as parameters (no global state)
- [ ] Input/output types are well-defined
- [ ] Behavior is identical to original code
- [ ] Unit tests pass for both old and new implementations
- [ ] Full backtest produces identical equity curve ±1e-6 tolerance
- [ ] Docstrings explain purpose, inputs, returns, and assumptions
- [ ] Parent module imports new module correctly
- [ ] No circular imports

### Behavior Preservation

Always verify behavior after refactoring:

```python
# Run before refactoring
equity_curve_before = run_portfolio_backtest()

# Make changes
# ...

# Run after refactoring
equity_curve_after = run_portfolio_backtest()

# Validate
tolerance = 1e-6
for i, (before, after) in enumerate(zip(equity_curve_before, equity_curve_after)):
    assert abs(before - after) < tolerance, \
        f"Equity curve diverged at index {i}: {before} vs {after}"
```

---

## Git Workflow

### Commit Message Format

```
[CATEGORY] Short description (50 chars max)

Detailed explanation (wrap at 72 chars):
- Explain the "why"
- Reference the architectural principle
- Note any behavior changes or parameter tweaks
- If refactoring: "Behavior verified identical" with backtest comparison

Examples:
[REFACTOR] Extract portfolio scoring into separate module
[FEATURE] Add market breadth filter to exposure scaling
[BUGFIX] Fix volatility ranking inversion in composite score
[CONFIG] Increase EXIT_RANK from 10 to 12 for better persistence
```

### Branch Naming

```
feature/add-scoring-module       # New features
bugfix/fix-equity-curve-rounding # Bug fixes
refactor/extract-portfolio-logic # Refactoring
experiment/test-ml-ranking       # Research experiments
docs/update-architecture         # Documentation
```

### PR Guidelines

1. **One concern per PR** — don't mix refactoring with feature changes
2. **Backtest comparison required** — show before/after equity curves
3. **Document behavior changes** — if metrics change, explain why
4. **Link to GitHub issues** — reference related issues in PR description

Example PR description:
```
## Description
Extract portfolio construction logic from portfolio_backtest.py 
into a new module to enable unit testing and reuse.

## Behavior Verification
- Full backtest run before: CAGR=12.5%, Sharpe=0.95, Max DD=-18.2%
- Full backtest run after: CAGR=12.5%, Sharpe=0.95, Max DD=-18.2%
- Trade-log verified identical (1,248 trades)
- ✅ Behavior preserved

## Tests Added
- test_portfolio_construction_respects_rank_limits
- test_portfolio_construction_enforces_sector_constraints
- test_construct_portfolio_calculates_turnover_correctly
```

---

## Python Style Guide

### PEP 8 Compliance

Follow PEP 8 with these project-specific notes:

- **Line length**: 79 characters for code, 88 acceptable for long strings
- **Indentation**: 4 spaces (never tabs)
- **Imports**: Group as: stdlib → third-party → local, alphabetically within groups
- **Naming**: snake_case for functions/variables, UPPER_CASE for constants

### Import Organization

```python
# Good: stdlib → third-party → local
import os
import sys
from datetime import datetime

import pandas as pd
import numpy as np
import yfinance as yf

from config import TOP_STOCKS, ENTRY_RANK
from indicators.indicators import calculate_indicators
from strategies.portfolio_construction import construct_portfolio
```

### Function & Variable Naming

```python
# Variables: descriptive, snake_case
current_holdings = []
monthly_turnover = []
risk_adjusted_scores = []

# Functions: verb + noun, snake_case
def calculate_metrics(returns):
def extract_stock_factors(df, date):
def construct_portfolio(ranked_stocks, current_holdings):

# Boolean functions: is_, has_, should_
def is_valid_indicator(df):
def has_missing_data(df):
def should_exit_position(rank, exit_rank):

# Constants: UPPER_CASE
BACKTEST_YEARS = 5
MAX_POSITION_WEIGHT = 0.30
RELATIVE_STRENGTH_LOOKBACK = 126
```

### Data Structure Conventions

```python
# Stock data: Dict[symbol, DataFrame]
stock_data = {
    "INFY": pd.DataFrame(...),
    "TCS": pd.DataFrame(...),
}

# Scored stocks: List[Dict] sorted by score
ranked_stocks = [
    {
        "Symbol": "INFY",
        "Score": 2.5,
        "Trend": 5.2,
        "RSI": 65.5,
        "Momentum": 12.3,
        "Volatility": 18.2,
        "Trend Rank": 0.95,
        # ...
    },
    # ...
]

# Holdings: List[str] (just symbols)
current_holdings = ["INFY", "TCS", "WIPRO"]

# Trade logs: List[Dict] with standardized keys
trade_logs = [
    {
        "Month": "2024-01-31",
        "Stock": "INFY",
        "Entry Price": 1800.50,
        "Exit Price": 1850.25,
        "Trade Return %": 2.76,
        "Stop Loss Hit": False,
    },
    # ...
]
```

### Code Organization Blocks

Use comment headers for section separation:

```python
# =====================================================
# SECTION NAME (50 chars + padding to 53)
# =====================================================

code here

# ===== SUBSECTION (50 chars + padding to 53)

code here
```

### Common Patterns

```python
# ✅ Idiomatic pandas
df["Rank"] = df["Score"].rank(pct=True)  # Percentile rank
df["Volatility Rank"] = 1 - df["Volatility"].rank(pct=True)  # Invert

# ✅ Safe getattr with default
sector = SECTOR_MAP.get(symbol, "Unknown")

# ✅ Early return for validation
if date not in df.index:
    return None
if pd.isna(dma_200):
    return None

# ✅ List comprehension for simple transformations
symbols = [stock["Symbol"] for stock in ranked_stocks]

# ✅ Boolean aggregation
any(x["Symbol"] == symbol for x in new_holdings)
all(key in d for key in required_keys)

# ❌ Avoid: Unnecessary complexity
result = [] 
for x in data:
    if condition:
        result.append(x)
# Use instead: [x for x in data if condition]
```

### Error Handling

```python
# ✅ DO: Handle expected conditions gracefully
if len(monthly_scores) == 0:
    return []  # Empty universe on this date

# ✅ DO: Use logging for diagnostics
import logging
logger = logging.getLogger(__name__)

logger.warning(f"No valid scores for {symbol} on {date}")

# ❌ DON'T: Silent failures
if error:
    pass  # Silently ignore

# ❌ DON'T: Generic exception catching
try:
    data = yf.download(symbol)
except:
    continue  # Unclear what error occurred
```

---

## Summary: Core Principles

1. **Modularity**: Each module has one clear responsibility
2. **Contracts**: Clear input/output types for all functions
3. **Configuration**: Centralize all parameters in `config.py`
4. **Reproducibility**: Behavior-preserving refactoring with backtest validation
5. **Documentation**: Docstrings explain "why", comments explain complex logic
6. **Testability**: Extract functions that can be unit tested
7. **Simplicity**: Use standard data structures (dict, DataFrame, list)
8. **Style**: Follow PEP 8 with consistency

---

## References

- [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [PEP 257 Docstring Conventions](https://www.python.org/dev/peps/pep-0257/)
- [Pandas Style Guide](https://pandas.pydata.org/docs/development/contributing.html)
- AlphaForge README: [Project Documentation](./README.md)
- Strategy Docs: [Strategy Architecture](./strategies/docs/)

---

**Last Updated**: 2026-06-26  
**Version**: 1.0  
**Maintained By**: AlphaForge Development Team
