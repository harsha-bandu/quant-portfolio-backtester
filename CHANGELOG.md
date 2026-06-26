# Changelog

All notable changes to **AlphaForge** will be documented in this file.

The format is inspired by **Keep a Changelog**, with additional sections for quantitative research findings and architectural evolution.

---

# [Unreleased]

Future changes and enhancements will be documented here.

---

# [1.0.0] - Initial Foundation Release

## Added

### Framework

* Modular project architecture
* Composite multi-factor scoring engine
* Portfolio construction engine
* Monthly portfolio rebalancing
* Holding persistence using ENTRY_RANK / EXIT_RANK
* Sector diversification constraints
* Dynamic market exposure scaling
* Risk-adjusted position sizing
* Transaction cost modelling
* Trade analytics
* Holdings history tracking
* Monthly performance reporting
* Benchmark comparison against NIFTY
* Portfolio analytics (CAGR, Sharpe Ratio, Drawdown, Volatility, Win Rate, Turnover)

### Engineering

* Configuration-driven framework
* Dedicated portfolio scoring module
* Dedicated portfolio construction module
* Excel reporting module
* Professional project folder structure
* Testing framework scaffold
* Copilot development guidelines
* Modular documentation structure

### Documentation

* README
* Architecture Guide
* Engineering Principles
* Project Manifesto
* Roadmap
* Development Guidelines

### Research

* Architecture review
* Workflow decomposition
* Portfolio backtest analysis
* Data flow documentation
* Research folder structure
* Experiment framework

---

## Changed

* Renamed project from **Screener** to **AlphaForge**
* Refactored project into a modular research framework
* Standardized folder structure for long-term maintainability
* Established documentation-first development workflow
* Separated portfolio scoring from workflow engine
* Separated portfolio construction from workflow engine

---

## Research Findings

### Accepted

* Composite multi-factor ranking
* Sector diversification
* Risk-adjusted weighting
* Holding persistence using ENTRY_RANK / EXIT_RANK
* Dynamic market exposure scaling
* Configuration-driven architecture
* Modular workflow decomposition

### Rejected

* ATR-based stop loss
* Hard market breadth filter

---

## Baseline Performance (v1.0.0)

| Metric                   |       Value |
| ------------------------ | ----------: |
| CAGR                     |      10.57% |
| Sharpe Ratio             |        0.37 |
| Volatility               |      13.63% |
| Max Drawdown             |     -22.59% |
| Average Monthly Return   |       0.92% |
| Win Rate                 |      50.00% |
| Average Turnover         |      93.88% |
| Average Holding Duration | 2.05 Months |

---

## Known Limitations

* Portfolio simulation remains part of the workflow engine and will be extracted in a future release.
* Portfolio metrics calculation is currently integrated within the workflow engine.
* Market data loading is tightly coupled to the backtest process and will be modularized in Version 2.

---

## Release Notes

AlphaForge v1.0.0 establishes the first stable foundation of the framework.

This release focuses on building a reproducible, modular, and extensible quantitative research platform rather than maximizing strategy performance.

Future releases will concentrate on architecture evolution, simulation modularization, portfolio optimization, walk-forward testing, machine learning integration, and AI-assisted quantitative research.
