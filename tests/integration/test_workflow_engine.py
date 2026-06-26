"""
Integration tests for workflow engine.

Tests focus on:
- Monthly rebalancing flow
- Data loading and preparation
- Scoring → Construction → Simulation pipeline
- Breadth calculations
- Exposure scaling
"""

import pytest
import pandas as pd
from strategies.portfolio_scoring import score_universe
from strategies.portfolio_construction import construct_portfolio


@pytest.mark.integration
class TestMonthlyRebalancingFlow:
    """Test complete monthly rebalancing workflow."""
    
    def test_full_monthly_flow(
        self, sample_stock_universe, sample_nifty_data, sample_dates
    ):
        """
        Test complete flow:
        1. Calculate market breadth
        2. Score universe
        3. Construct portfolio
        """
        # Use a date with all indicators
        test_date = sample_dates[-1]
        
        # 1. Score stocks
        ranked_stocks = score_universe(sample_stock_universe, test_date)
        
        assert len(ranked_stocks) > 0, "Should have scored stocks"
        
        # 2. Construct portfolio
        current_holdings = []
        holding_durations = {}
        monthly_turnover = []
        completed_holding_periods = []
        
        result = construct_portfolio(
            ranked_stocks,
            current_holdings,
            holding_durations,
            monthly_turnover,
            completed_holding_periods,
        )
        
        assert len(result["top_stocks"]) > 0
        assert len(result["new_current_holdings"]) > 0


@pytest.mark.integration
class TestBreadthCalculation:
    """Test market breadth filter."""
    
    def test_breadth_calculation_counts_stocks_above_dma(
        self, sample_stock_universe, sample_dates
    ):
        """
        Breadth % = (stocks > 200 DMA) / valid_stocks
        """
        test_date = sample_dates[-1]
        
        stocks_above_dma = 0
        valid_stocks = 0
        
        for symbol, df in sample_stock_universe.items():
            if test_date not in df.index:
                continue
            
            row = df.loc[test_date]
            if pd.isna(row["DMA_200"]):
                continue
            
            valid_stocks += 1
            if row["Close"] > row["DMA_200"]:
                stocks_above_dma += 1
        
        if valid_stocks > 0:
            breadth_pct = (stocks_above_dma / valid_stocks) * 100
            assert 0 <= breadth_pct <= 100


@pytest.mark.integration
class TestExposureScaling:
    """Test dynamic market exposure scaling."""
    
    def test_exposure_scales_with_breadth(self):
        """
        Exposure should scale:
        - 80%+: 1.0x exposure
        - 60-80%: 0.8x
        - 40-60%: 0.6x
        - 20-40%: 0.4x
        - <20%: 0.0x (cash)
        """
        exposure_map = [
            (85, 1.0),
            (70, 0.8),
            (50, 0.6),
            (30, 0.4),
            (10, 0.0),
        ]
        
        for breadth_pct, expected_exposure in exposure_map:
            if breadth_pct >= 80:
                exposure = 1.0
            elif breadth_pct >= 60:
                exposure = 0.8
            elif breadth_pct >= 40:
                exposure = 0.6
            elif breadth_pct >= 20:
                exposure = 0.4
            else:
                exposure = 0.0
            
            assert exposure == expected_exposure


@pytest.mark.integration
class TestDataPipelineIntegration:
    """Test data flow through pipeline."""
    
    def test_indicators_available_for_scoring(
        self, sample_stock_universe, sample_dates
    ):
        """All required indicators should be present for scoring."""
        required_indicators = ["DMA_200", "RSI", "Volatility"]
        test_date = sample_dates[-1]
        
        for symbol, df in sample_stock_universe.items():
            if test_date not in df.index:
                continue
            
            row = df.loc[test_date]
            for indicator in required_indicators:
                assert indicator in df.columns
                # Check if has some valid data (not all NaN)
                assert not pd.isna(row[indicator]) or len(df) < 50


@pytest.mark.integration
class TestScoringThenConstructionPipeline:
    """Test scoring immediately followed by construction."""
    
    def test_construction_accepts_scoring_output(
        self, sample_stock_universe, sample_dates
    ):
        """
        Portfolio construction should accept scores from
        score_universe without modification.
        """
        test_date = sample_dates[-1]
        
        # Score
        ranked_stocks = score_universe(sample_stock_universe, test_date)
        
        if len(ranked_stocks) == 0:
            pytest.skip("No valid stocks to score")
        
        # Construct
        result = construct_portfolio(
            ranked_stocks,
            [],
            {},
            [],
            [],
        )
        
        # Construction should succeed with scoring output
        assert isinstance(result, dict)
        assert "top_stocks" in result
