# AlphaForge Test Suite Guide

## Directory Structure

```
tests/
├── __init__.py                 # Test package marker
├── conftest.py                 # Shared fixtures for all tests
├── pytest.ini                  # PyTest configuration
│
├── unit/                       # Unit tests (fast, isolated)
│   ├── __init__.py
│   ├── test_portfolio_scoring.py        # score_universe(), factor extraction
│   ├── test_portfolio_construction.py   # construct_portfolio(), rank filtering
│   └── test_metrics.py                  # CAGR, Sharpe, max drawdown calculations
│
├── integration/                # Integration tests (components together)
│   ├── __init__.py
│   ├── test_workflow_engine.py          # Monthly rebalancing flow
│   ├── test_portfolio_constraints.py    # Rank + sector + size constraints
│   └── test_equity_curve.py             # Position sizing, P&L, weighting
│
└── regression/                 # Regression tests (behavior preservation)
    ├── __init__.py
    └── test_full_backtest_regression.py # Golden copy validation
```

## Test Organization

### Unit Tests (`tests/unit/`)
- **Focus**: Individual functions and components in isolation
- **Speed**: < 100ms per test
- **Scope**: Single module only
- **Examples**:
  - `test_portfolio_scoring.py`: Factor extraction, normalization, scoring
  - `test_portfolio_construction.py`: Rank filtering, sector constraints
  - `test_metrics.py`: CAGR, Sharpe, max drawdown calculations

### Integration Tests (`tests/integration/`)
- **Focus**: Multi-component workflows
- **Speed**: 100ms to 1 second per test
- **Scope**: 2+ modules working together
- **Examples**:
  - `test_workflow_engine.py`: Score → Construct → Simulate pipeline
  - `test_portfolio_constraints.py`: Rank + sector + turnover together
  - `test_equity_curve.py`: Position sizing, weighting, P&L calculations

### Regression Tests (`tests/regression/`)
- **Focus**: Behavior preservation after refactoring
- **Speed**: 10+ seconds per test
- **Scope**: Full backtest end-to-end
- **Examples**:
  - `test_full_backtest_regression.py`: Golden copy comparison
  - Trade log validation
  - Equity curve consistency checks

## Shared Fixtures (conftest.py)

### Market Data Fixtures
- `sample_dates`: 252 trading days
- `sample_ohlcv_data`: Realistic price movement
- `sample_indicators_data`: With DMA_200, RSI, ATR, Volatility
- `sample_stock_universe`: 5-symbol universe
- `sample_nifty_data`: NIFTY50 index data

### Portfolio State Fixtures
- `initial_portfolio_state`: Empty portfolio variables
- `sample_ranked_stocks`: Pre-scored 5 stocks (sorted by Score)
- `sample_current_holdings`: ["INFY", "TCS"]
- `sample_holding_durations`: {"INFY": 3, "TCS": 1}

### Configuration Fixtures
- `mock_config`: Monkeypatch config parameters for testing

### Utility Fixtures
- `temp_output_dir`: Temp directory for test outputs
- `sample_trade_log`: Sample trade execution records
- `sample_holdings_history`: Sample portfolio holdings history

## Running Tests

### Run all tests
```bash
pytest tests/
```

### Run only unit tests
```bash
pytest tests/unit/ -m unit
```

### Run only integration tests
```bash
pytest tests/integration/ -m integration
```

### Run only regression tests
```bash
pytest tests/regression/ -m regression
```

### Run specific test class
```bash
pytest tests/unit/test_portfolio_scoring.py::TestFactorExtraction
```

### Run specific test
```bash
pytest tests/unit/test_portfolio_scoring.py::TestFactorExtraction::test_extract_factors_returns_dict_with_required_keys
```

### Run excluding slow tests
```bash
pytest tests/ -m "not slow"
```

### Run with verbose output
```bash
pytest tests/ -v
```

### Run with coverage report
```bash
pytest tests/ --cov=strategies --cov=analytics --cov=reporting --cov-report=html
```

### Run in parallel (requires pytest-xdist)
```bash
pytest tests/ -n auto
```

### Run with timing information
```bash
pytest tests/ --durations=10
```

## Test Markers

Use markers to categorize and filter tests:

```python
@pytest.mark.unit
def test_something():
    pass

@pytest.mark.integration
def test_something_else():
    pass

@pytest.mark.regression
def test_full_backtest():
    pass

@pytest.mark.slow
def test_long_running():
    pass
```

### Filter by marker
```bash
pytest -m "unit"           # Only unit tests
pytest -m "integration"    # Only integration tests
pytest -m "regression"     # Only regression tests
pytest -m "not slow"       # Exclude slow tests
pytest -m "unit or integration"  # Unit OR integration
```

## Test Development Workflow

### 1. Write failing test first
```python
@pytest.mark.unit
def test_new_feature():
    result = new_function(sample_data)
    assert result == expected
```

### 2. Run to confirm it fails
```bash
pytest tests/unit/test_new.py::test_new_feature -v
```

### 3. Implement feature
```python
def new_function(data):
    return computed_result
```

### 4. Run again to confirm it passes
```bash
pytest tests/unit/test_new.py::test_new_feature -v
```

### 5. Add edge case tests
```python
@pytest.mark.unit
@pytest.mark.parametrize("invalid_input", [None, "", []])
def test_new_feature_with_invalid_input(invalid_input):
    result = new_function(invalid_input)
    assert result is None
```

### 6. Run full test suite before commit
```bash
pytest tests/ -m "not slow" -v
```

## Common Patterns

### Using fixtures
```python
def test_something(sample_stock_universe, sample_dates):
    """Fixtures are automatically injected."""
    ranked = score_universe(sample_stock_universe, sample_dates[-1])
    assert len(ranked) > 0
```

### Parametrized tests
```python
@pytest.mark.parametrize("price,dma,expected", [
    (1100, 1000, True),   # Price > DMA
    (900, 1000, False),   # Price < DMA
    (1000, 1000, False),  # Price = DMA
])
def test_dma_filter(price, dma, expected):
    result = passes_dma_filter(price, dma)
    assert result == expected
```

### Mocking config
```python
def test_with_custom_config(mock_config):
    mock_config["TOP_STOCKS"] = 3
    # Test with custom TOP_STOCKS
```

## Continuous Integration

For GitHub Actions / CI/CD pipelines:

```bash
# Run all tests with coverage
pytest tests/ --cov=strategies --cov-report=xml

# Exit with error if any failed
pytest tests/ --tb=short

# Run with timeout
pytest tests/ --timeout=60
```

## Troubleshooting

### "ModuleNotFoundError" for imports
```bash
# Ensure you're in project root
cd /path/to/AlphaForge

# Run pytest from project root
pytest tests/
```

### Fixtures not found
```bash
# Verify conftest.py is in tests/ directory
# Fixtures are auto-discovered by pytest
```

### Test database/file pollution
```bash
# Use temp_output_dir fixture to avoid conflicts
def test_export(temp_output_dir):
    output_file = temp_output_dir / "results.xlsx"
    # Use temp_output_dir for all file operations
```

## References

- [pytest documentation](https://docs.pytest.org/)
- [pytest fixtures](https://docs.pytest.org/en/latest/how-to/fixtures.html)
- [pytest markers](https://docs.pytest.org/en/latest/how-to/mark.html)
- AlphaForge copilot-instructions.md: Testing & Validation section
