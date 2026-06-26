# AlphaForge Research

The `research` directory contains all quantitative research performed using AlphaForge.

Unlike traditional backtesting projects, AlphaForge treats every strategy enhancement as a scientific experiment.

Every experiment follows a reproducible workflow:

```
Idea
   ↓
Hypothesis
   ↓
Implementation
   ↓
Backtest
   ↓
Analysis
   ↓
Conclusion
   ↓
Acceptance / Rejection
```

---

## Directory Structure

```
research/

    baselines/
        Accepted benchmark versions

    experiments/
        Individual experiment folders

    reports/
        Generated research reports

    templates/
        Standard experiment templates
```

---

## Experiment Philosophy

Every experiment should answer a question.

Examples:

* Does Dynamic Exposure improve Sharpe Ratio?
* Does Volatility Targeting reduce drawdown?
* Does Machine Learning outperform factor ranking?

If a question cannot be answered objectively, it should not become part of the framework.

---

## Baselines

Accepted framework versions become baselines.

Future experiments are always compared against the latest accepted baseline.

This ensures every improvement is measurable.

---

## Reproducibility

Every experiment should preserve:

* Configuration
* Metrics
* Holdings
* Trades
* Charts
* Observations
* Final conclusion

Future researchers should be able to reproduce historical experiments using only the stored artifacts.

---

## Goal

The purpose of AlphaForge Research is not simply to discover profitable strategies.

Its purpose is to build a repeatable, evidence-driven research process.
