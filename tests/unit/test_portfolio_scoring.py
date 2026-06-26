"""
Unit tests for portfolio_scoring module.

Tests focus on:
- Factor extraction and validation
- Factor normalization
- Composite score calculation
- Ranking behavior
"""

import pytest
import pandas as pd
import numpy as np
from strategies.portfolio_scoring import extract_stock_factors, score_universe


@pytest.mark.unit
class TestFactorExtraction:
    """Test individual factor extraction."""
    
    def test_extract_factors_returns_dict_with_required_keys(
        self, sample_indicators_data
    ):
        """
        Factor extraction should return dict with
        Trend, RSI, Momentum, Volatility keys.
        """
        # Use date where all indicators exist
        test_date = sample_indicators_data.index[-1]
        
        factors = extract_stock_factors(sample_indicators_data, test_date)
        
        if factors is not None:
            assert isinstance(factors, dict)
            assert set(factors.keys()) == {
                "Trend", "RSI", "Momentum", "Volatility"
            }
    
    def test_extract_factors_returns_none_for_invalid_date(
        self, sample_indicators_data
    ):
        """Should return None if date not in DataFrame."""
        invalid_date = pd.Timestamp("1900-01-01")
        
        factors = extract_stock_factors(sample_indicators_data, invalid_date)
        
        assert factors is None
    
    def test_extract_factors_returns_none_if_price_below_dma200(
        self, sample_indicators_data
    ):
        """Should return None if price not above 200 DMA (downtrend)."""
        # TODO: Implement after understanding indicator calculation
        pass
    
    def test_extract_factors_returns_none_if_missing_indicators(
        self, sample_indicators_data
    ):
        """Should return None if required indicators are NaN."""
        # TODO: Implement after understanding indicator calculation
        pass
    
    def test_factor_values_are_numeric(self, sample_indicators_data):
        """All factor values should be numeric."""
        test_date = sample_indicators_data.index[-1]
        
        factors = extract_stock_factors(sample_indicators_data, test_date)
        
        if factors is not None:
            for key, value in factors.items():
                assert isinstance(value, (int, float, np.number))


@pytest.mark.unit
class TestScoreUniverse:
    """Test universe scoring and ranking."""
    
    def test_score_universe_returns_list(
        self, sample_stock_universe, sample_dates
    ):
        """Should return list of scored stocks."""
        test_date = sample_dates[-1]
        
        ranked = score_universe(sample_stock_universe, test_date)
        
        assert isinstance(ranked, list)
    
    def test_score_universe_returns_empty_list_for_no_valid_stocks(
        self, sample_stock_universe
    ):
        """Should return empty list if no stocks meet criteria."""
        invalid_date = pd.Timestamp("1900-01-01")
        
        ranked = score_universe(sample_stock_universe, invalid_date)
        
        assert ranked == []
    
    def test_ranked_stocks_sorted_by_score_descending(
        self, sample_stock_universe, sample_dates
    ):
        """Returned list should be sorted by Score (highest first)."""
        test_date = sample_dates[-1]
        
        ranked = score_universe(sample_stock_universe, test_date)
        
        if len(ranked) > 1:
            scores = [stock["Score"] for stock in ranked]
            assert scores == sorted(scores, reverse=True)
    
    def test_ranked_stocks_include_required_fields(
        self, sample_stock_universe, sample_dates
    ):
        """Each ranked stock should have required fields."""
        test_date = sample_dates[-1]
        required_fields = {
            "Symbol", "Score", "Trend", "RSI", "Momentum", "Volatility",
            "Trend Rank", "RSI Rank", "Momentum Rank", "Volatility Rank"
        }
        
        ranked = score_universe(sample_stock_universe, test_date)
        
        for stock in ranked:
            assert required_fields.issubset(set(stock.keys()))
    
    def test_percentile_ranks_are_between_0_and_1(
        self, sample_stock_universe, sample_dates
    ):
        """All percentile ranks should be in [0, 1] range."""
        test_date = sample_dates[-1]
        rank_keys = ["Trend Rank", "RSI Rank", "Momentum Rank", 
                     "Volatility Rank"]
        
        ranked = score_universe(sample_stock_universe, test_date)
        
        for stock in ranked:
            for rank_key in rank_keys:
                assert 0 <= stock[rank_key] <= 1


@pytest.mark.unit
class TestCompositeScore:
    """Test composite score calculation."""
    
    def test_composite_score_is_positive(
        self, sample_stock_universe, sample_dates
    ):
        """Composite score should be >= 0."""
        test_date = sample_dates[-1]
        
        ranked = score_universe(sample_stock_universe, test_date)
        
        for stock in ranked:
            assert stock["Score"] >= 0
    
    def test_volatility_inversion_lower_vol_higher_score(
        self, sample_stock_universe, sample_dates
    ):
        """Lower volatility should result in higher rank."""
        # TODO: Implement after confirming volatility behavior
        pass
    
    def test_score_consistency_across_calls(
        self, sample_stock_universe, sample_dates
    ):
        """Same inputs should produce identical scores."""
        test_date = sample_dates[-1]
        
        ranked1 = score_universe(sample_stock_universe, test_date)
        ranked2 = score_universe(sample_stock_universe, test_date)
        
        assert ranked1 == ranked2


@pytest.mark.unit
@pytest.mark.parametrize("empty_field", [
    "DMA_200", "RSI", "Volatility"
])
def test_extract_factors_missing_required_fields(
    sample_indicators_data, empty_field
):
    """Should return None if required indicator is missing."""
    df = sample_indicators_data.copy()
    test_date = df.index[-1]
    
    # Remove field to simulate missing data
    df[empty_field] = np.nan
    
    factors = extract_stock_factors(df, test_date)
    
    assert factors is None
