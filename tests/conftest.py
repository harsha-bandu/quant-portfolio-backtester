"""
Shared pytest fixtures for AlphaForge test suite.

Provides:
- Sample market data (OHLCV)
- Calculated indicators
- Portfolio state objects
- Configuration mocking
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


# =====================================================
# MARKET DATA FIXTURES
# =====================================================

@pytest.fixture
def sample_dates():
    """Generate 252 trading days (1 year) of sample dates."""
    end_date = pd.Timestamp("2024-12-31")
    start_date = end_date - pd.Timedelta(days=365)
    return pd.bdate_range(start=start_date, end=end_date)


@pytest.fixture
def sample_ohlcv_data(sample_dates):
    """
    Generate realistic OHLCV data for a single stock.
    
    Returns:
        pd.DataFrame with columns: Open, High, Low, Close, Volume
    """
    np.random.seed(42)
    n = len(sample_dates)
    
    # Simulate realistic price movement
    returns = np.random.normal(0.0005, 0.015, n)
    prices = 1000 * np.cumprod(1 + returns)
    
    df = pd.DataFrame({
        "Open": prices * (1 + np.random.normal(0, 0.005, n)),
        "High": prices * (1 + np.abs(np.random.normal(0, 0.008, n))),
        "Low": prices * (1 - np.abs(np.random.normal(0, 0.008, n))),
        "Close": prices,
        "Volume": np.random.randint(1e6, 1e8, n),
    }, index=sample_dates)
    
    return df


@pytest.fixture
def sample_indicators_data(sample_ohlcv_data):
    """
    Generate sample data with calculated indicators.
    
    Adds: DMA_200, RSI, ATR, Volatility
    """
    df = sample_ohlcv_data.copy()
    
    # Simple DMA_200 (not mathematically perfect, just for testing)
    df["DMA_200"] = df["Close"].rolling(window=200).mean()
    
    # Simple RSI (14-period)
    delta = df["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))
    
    # Simple ATR (14-period)
    high_low = df["High"] - df["Low"]
    high_close = np.abs(df["High"] - df["Close"].shift())
    low_close = np.abs(df["Low"] - df["Close"].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    df["ATR"] = true_range.rolling(window=14).mean()
    
    # Simple Volatility (20-period rolling std of returns)
    df["Volatility"] = df["Close"].pct_change().rolling(window=20).std()
    
    return df


@pytest.fixture
def sample_stock_universe(sample_indicators_data):
    """
    Generate sample stock data for multiple symbols.
    
    Returns:
        Dict[str, pd.DataFrame] with 5 sample stocks
    """
    symbols = ["INFY", "TCS", "WIPRO", "RELIANCE", "HDFC"]
    stock_data = {}
    
    for i, symbol in enumerate(symbols):
        # Add slight variation per symbol
        df = sample_indicators_data.copy()
        multiplier = 1.0 + (i * 0.1)  # Different price levels
        for col in ["Open", "High", "Low", "Close"]:
            df[col] = df[col] * multiplier
        stock_data[symbol] = df
    
    return stock_data


@pytest.fixture
def sample_nifty_data(sample_indicators_data):
    """Generate sample NIFTY50 index data."""
    return sample_indicators_data.copy()


# =====================================================
# PORTFOLIO STATE FIXTURES
# =====================================================

@pytest.fixture
def initial_portfolio_state():
    """
    Initialize empty portfolio state.
    
    Returns:
        Dict with portfolio tracking variables
    """
    return {
        "current_holdings": [],
        "holding_durations": {},
        "completed_holding_periods": [],
        "monthly_turnover": [],
        "equity_curve": [100],
        "portfolio_returns": [],
        "trade_logs": [],
        "holdings_history": [],
    }


@pytest.fixture
def sample_ranked_stocks():
    """
    Generate sample scored and ranked stocks.
    
    Returns:
        List[Dict] with scoring factors, ranked by composite score
    """
    stocks = [
        {
            "Symbol": "INFY",
            "Trend": 5.2,
            "RSI": 65.5,
            "Momentum": 12.3,
            "Volatility": 18.2,
            "Trend Rank": 0.95,
            "RSI Rank": 0.88,
            "Momentum Rank": 0.92,
            "Volatility Rank": 0.80,
            "Score": 3.55,
        },
        {
            "Symbol": "TCS",
            "Trend": 4.1,
            "RSI": 62.0,
            "Momentum": 9.8,
            "Volatility": 16.5,
            "Trend Rank": 0.85,
            "RSI Rank": 0.75,
            "Momentum Rank": 0.80,
            "Volatility Rank": 0.85,
            "Score": 3.25,
        },
        {
            "Symbol": "WIPRO",
            "Trend": 3.5,
            "RSI": 58.0,
            "Momentum": 7.2,
            "Volatility": 20.1,
            "Trend Rank": 0.70,
            "RSI Rank": 0.62,
            "Momentum Rank": 0.65,
            "Volatility Rank": 0.70,
            "Score": 2.67,
        },
        {
            "Symbol": "RELIANCE",
            "Trend": 2.8,
            "RSI": 55.0,
            "Momentum": 5.5,
            "Volatility": 22.3,
            "Trend Rank": 0.55,
            "RSI Rank": 0.50,
            "Momentum Rank": 0.50,
            "Volatility Rank": 0.60,
            "Score": 2.15,
        },
        {
            "Symbol": "HDFC",
            "Trend": 1.5,
            "RSI": 52.0,
            "Momentum": 3.2,
            "Volatility": 25.0,
            "Trend Rank": 0.40,
            "RSI Rank": 0.40,
            "Momentum Rank": 0.35,
            "Volatility Rank": 0.50,
            "Score": 1.65,
        },
    ]
    return sorted(stocks, key=lambda x: x["Score"], reverse=True)


@pytest.fixture
def sample_current_holdings():
    """Sample current portfolio holdings."""
    return ["INFY", "TCS"]


@pytest.fixture
def sample_holding_durations():
    """Sample holding duration tracking."""
    return {
        "INFY": 3,
        "TCS": 1,
    }


# =====================================================
# CONFIGURATION FIXTURES
# =====================================================

@pytest.fixture
def mock_config(monkeypatch):
    """
    Mock config parameters for testing.
    
    Usage:
        def test_something(mock_config):
            mock_config["TOP_STOCKS"] = 3
            # Test with custom config
    """
    config_values = {
        "TOP_STOCKS": 5,
        "ENTRY_RANK": 5,
        "EXIT_RANK": 12,
        "MAX_STOCKS_PER_SECTOR": 2,
        "STOP_LOSS_PCT": 10,
        "MAX_POSITION_WEIGHT": 0.30,
        "RSI_WEIGHT": 25,
        "TREND_WEIGHT": 12,
        "RELATIVE_STRENGTH_WEIGHT": 4,
        "VOLATILITY_PENALTY_WEIGHT": 4,
        "RISK_FREE_RATE": 6,
    }
    
    # Apply monkeypatch for config imports
    import config
    for key, value in config_values.items():
        monkeypatch.setattr(config, key, value)
    
    return config_values


# =====================================================
# UTILITY FIXTURES
# =====================================================

@pytest.fixture
def temp_output_dir(tmp_path):
    """
    Provide temporary directory for test outputs.
    
    Usage:
        def test_export(temp_output_dir):
            output_file = temp_output_dir / "results.xlsx"
            # Test writes results
    """
    return tmp_path


@pytest.fixture
def sample_trade_log():
    """Sample trade execution records."""
    return [
        {
            "Month": "2024-01-31",
            "Stock": "INFY",
            "Entry Price": 1800.50,
            "Exit Price": 1850.25,
            "Trade Return %": 2.76,
            "Score": 3.55,
            "Gross Return %": 2.76,
            "Net Return %": 2.56,
            "Stop Loss Hit": False,
        },
        {
            "Month": "2024-01-31",
            "Stock": "TCS",
            "Entry Price": 3200.00,
            "Exit Price": 3100.00,
            "Trade Return %": -3.13,
            "Score": 3.25,
            "Gross Return %": -3.13,
            "Net Return %": -3.33,
            "Stop Loss Hit": True,
        },
    ]


@pytest.fixture
def sample_holdings_history():
    """Sample portfolio holdings history."""
    return [
        {
            "Month": "2024-01-31",
            "Stock": "INFY",
            "Sector": "IT",
            "Score": 3.55,
            "Weight": 22.5,
        },
        {
            "Month": "2024-01-31",
            "Stock": "TCS",
            "Sector": "IT",
            "Score": 3.25,
            "Weight": 20.0,
        },
    ]


# =====================================================
# PYTEST CONFIGURATION
# =====================================================

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "regression: mark test as a regression test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
