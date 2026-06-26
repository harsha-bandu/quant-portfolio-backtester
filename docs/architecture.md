# Quant Portfolio Research Framework

## Software Architecture

**Version:** 1.0
**Status:** Living Document
**Last Updated:** June 2026

---

# 1. Vision

The goal of this project is **not** to build a single trading strategy.

The goal is to build a reusable, extensible **Quantitative Portfolio Research Framework** capable of supporting multiple investment strategies, robust research workflows, and institutional-grade portfolio analytics.

The framework should enable experimentation without requiring architectural rewrites as new features are introduced.

---

# 2. Design Philosophy

The framework follows five guiding principles.

## 2.1 Separation of Concerns

Each module should have one clear responsibility.

Examples:

* Data acquisition
* Factor generation
* Portfolio construction
* Risk management
* Trade simulation
* Performance analytics
* Reporting

No module should own responsibilities outside its domain.

---

## 2.2 Pipeline-Oriented Architecture

The system follows a sequential research pipeline.

```
Market Data
      ↓
Indicator Calculation
      ↓
Factor Scoring
      ↓
Ranking
      ↓
Portfolio Construction
      ↓
Risk Management
      ↓
Trade Simulation
      ↓
Performance Analytics
      ↓
Reporting
```

Each stage receives the output of the previous stage and produces a well-defined artifact.

---

## 2.3 Configuration Driven

Strategy behaviour should be controlled through configuration rather than code changes.

Examples include:

* Universe
* Rebalance frequency
* Portfolio size
* Factor weights
* Transaction costs
* Risk parameters
* Position sizing

---

## 2.4 Research First

Every enhancement should be treated as an experiment.

Implementation alone is not sufficient.

Every feature must be:

* implemented
* backtested
* compared against baseline
* documented
* accepted or rejected

---

## 2.5 Incremental Evolution

Large rewrites are avoided.

Architecture evolves gradually by extracting responsibilities into dedicated modules while preserving behaviour.

---

# 3. Current Architecture

The framework currently consists of the following logical stages.

```
Entry Point
      │
      ▼
Portfolio Backtest
      │
      ▼
Historical Data Download
      │
      ▼
Indicator Calculation
      │
      ▼
Monthly Rebalance Engine
      │
      ▼
Factor Ranking
      │
      ▼
Portfolio Construction
      │
      ▼
Risk Controls
      │
      ▼
Trade Simulation
      │
      ▼
Performance Metrics
      │
      ▼
Reporting
```

The implementation is currently centered around `portfolio_backtest.py`, which orchestrates the entire workflow.

Although functional, this module currently contains multiple business responsibilities and will be decomposed gradually.

---

# 4. Target Architecture

The long-term target architecture is based on independent engines.

```
                     Quant Research Framework

        Configuration
              │
              ▼
        Data Engine
              │
              ▼
      Indicator Engine
              │
              ▼
       Strategy Engine
              │
              ▼
      Portfolio Engine
              │
              ▼
         Risk Engine
              │
              ▼
      Execution Engine
              │
              ▼
      Analytics Engine
              │
              ▼
      Reporting Engine
              │
              ▼
      Research Engine
```

Each engine owns one business capability.

---

# 5. Engine Responsibilities

## Data Engine

Responsible for:

* historical data loading
* benchmark loading
* caching
* calendar generation
* future data providers

---

## Indicator Engine

Responsible for:

* RSI
* Moving averages
* Momentum
* Volatility
* ATR
* Future technical indicators

---

## Strategy Engine

Responsible for:

* factor extraction
* normalization
* composite ranking
* future ML ranking models

This engine decides **what to buy**.

---

## Portfolio Engine

Responsible for:

* stock selection
* holding persistence
* sector constraints
* portfolio allocation

This engine decides **how the portfolio is built**.

---

## Risk Engine

Responsible for:

* exposure scaling
* volatility targeting
* stop loss
* position limits
* risk budgeting

This engine decides **how much risk to take**.

---

## Execution Engine

Responsible for:

* trade simulation
* transaction costs
* portfolio returns
* trade logging

---

## Analytics Engine

Responsible for:

* CAGR
* Sharpe
* Drawdown
* Turnover
* Holding duration
* Future factor attribution

---

## Reporting Engine

Responsible for:

* charts
* Excel exports
* HTML reports
* PDF reports
* dashboards

---

## Research Engine

Responsible for:

* experiment tracking
* baseline comparison
* parameter sensitivity
* walk-forward testing
* Monte Carlo
* optimization
* experiment reports

---

# 6. Architectural Decisions

## ADL-001

Separate user-facing entry points are retained.

Current entry points:

* main.py
* run_backtest.py
* run_portfolio_backtest.py

These remain lightweight orchestration scripts.

---

## ADL-002

The project will use incremental refactoring.

Large rewrites are avoided.

Every new feature should extract the logic it touches into a dedicated module.

---

## ADL-003

Business capability determines module ownership.

New features are assigned to an engine rather than appended to the existing backtest module.

---

# 7. Coding Standards

Every new module should:

* have one responsibility
* expose a clean public interface
* avoid side effects
* avoid direct plotting
* avoid direct file exports
* avoid hidden configuration

---

# 8. Research Standards

Every experiment should include:

* configuration snapshot
* performance metrics
* holdings
* trades
* charts
* observations
* conclusion

Accepted experiments become new baselines.

Rejected experiments remain archived for future reference.

---

# 9. Roadmap

## Phase 1

Standard Portfolio Framework

Current focus:

* Dynamic Exposure Scaling
* Adaptive Position Sizing
* Volatility Targeting
* Portfolio Optimizers
* Professional Reporting

---

## Phase 2

Research Platform

* Walk-forward optimization
* Monte Carlo simulation
* Parameter robustness
* Factor attribution
* Experiment manager

---

## Phase 3

Institutional Platform

* Machine Learning Ranking
* Regime Detection
* Multi-strategy portfolios
* Risk decomposition
* Alternative data

---

## Phase 4

Agentic Quant Platform

* Research Agent
* Optimization Agent
* Portfolio Manager
* Report Generator
* AI-assisted strategy development

---

# 10. Long-Term Objective

The framework should eventually support the complete lifecycle of quantitative research.

```
Research Idea
      ↓
Implementation
      ↓
Backtest
      ↓
Experiment Tracking
      ↓
Comparison
      ↓
Optimization
      ↓
Validation
      ↓
Deployment
```

The architecture should evolve continuously while preserving modularity, reproducibility, and research integrity.
