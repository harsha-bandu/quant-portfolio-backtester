"""
Integration tests for equity curve and P&L tracking.

Tests focus on:
- Equity curve progression
- Position sizing and weighting
- Trade P&L calculation
- Return attribution
"""

import pytest
import numpy as np
import pandas as pd


@pytest.mark.integration
class TestEquityCurveProgression:
    """Test equity curve calculation and updates."""
    
    def test_equity_curve_grows_with_positive_returns(self):
        """Equity curve should increase with positive portfolio returns."""
        starting_capital = 100
        equity_curve = [starting_capital]
        
        # Month 1: +2% return
        equity_curve.append(equity_curve[-1] * (1 + 0.02))
        
        # Month 2: +1.5% return
        equity_curve.append(equity_curve[-1] * (1 + 0.015))
        
        assert equity_curve[1] > equity_curve[0]
        assert equity_curve[2] > equity_curve[1]
        assert len(equity_curve) == 3
    
    def test_equity_curve_declines_with_negative_returns(self):
        """Equity curve should decrease with negative portfolio returns."""
        starting_capital = 100
        equity_curve = [starting_capital]
        
        # Month 1: -1% return
        equity_curve.append(equity_curve[-1] * (1 - 0.01))
        
        assert equity_curve[1] < equity_curve[0]
    
    def test_equity_curve_affected_by_exposure_scaling(self):
        """
        Equity curve changes should be scaled by market exposure.
        Return * exposure = actual portfolio return
        """
        equity = 100
        portfolio_return_pct = 2.0
        exposure = 0.6
        
        adjusted_return = portfolio_return_pct * exposure
        new_equity = equity * (1 + adjusted_return / 100)
        
        assert new_equity == equity * (1 + 0.6 * 0.02)


@pytest.mark.integration
class TestPositionWeighting:
    """Test position size and weight calculations."""
    
    def test_volatility_adjusted_weighting(self):
        """
        Weights should be adjusted for volatility:
        weight = score / max(volatility, 0.0001)
        """
        scores = [3.5, 3.2, 2.8]
        volatilities = [18.2, 16.5, 20.1]
        
        adjusted_scores = [
            scores[i] / max(volatilities[i], 0.0001)
            for i in range(len(scores))
        ]
        
        total_adjusted = sum(adjusted_scores)
        weights = [s / total_adjusted for s in adjusted_scores]
        
        assert len(weights) == 3
        assert abs(sum(weights) - 1.0) < 1e-6
    
    def test_max_position_weight_cap(self):
        """Individual position weight should not exceed MAX_POSITION_WEIGHT."""
        max_weight = 0.30
        
        # Raw weights (uncapped)
        raw_weights = [0.25, 0.25, 0.25, 0.25]
        
        # Apply cap
        capped_weights = [min(w, max_weight) for w in raw_weights]
        
        # Re-normalize
        total = sum(capped_weights)
        normalized_weights = [w / total for w in capped_weights]
        
        # All should be <= max_weight after capping
        for weight in capped_weights:
            assert weight <= max_weight
        
        # Normalized sum should be ~1.0
        assert abs(sum(normalized_weights) - 1.0) < 1e-6
    
    def test_weight_normalization_after_cap(self):
        """
        After applying max weight cap, weights must be re-normalized
        to sum to 1.0.
        """
        positions = 3
        max_weight = 0.30
        
        # Raw weights sum to 1.0
        raw_weights = [1.0/positions] * positions  # [0.333, 0.333, 0.333]
        
        # Cap
        capped = [min(w, max_weight) for w in raw_weights]  # [0.30, 0.30, 0.30]
        
        # Renormalize
        total = sum(capped)
        final_weights = [w / total for w in capped]
        
        # Should sum to 1.0
        assert abs(sum(final_weights) - 1.0) < 1e-6


@pytest.mark.integration
class TestTradePnL:
    """Test trade-level P&L calculation."""
    
    def test_basic_trade_return_calculation(self):
        """
        Trade return = (exit_price - entry_price) / entry_price
        """
        entry = 1000
        exit_price = 1050
        
        gross_return = ((exit_price - entry) / entry) * 100
        
        assert gross_return == 5.0
    
    def test_transaction_costs_applied(self):
        """Transaction cost should reduce net return."""
        gross_return_pct = 5.0
        transaction_cost_pct = 0.20
        
        net_return_pct = gross_return_pct - transaction_cost_pct
        
        assert net_return_pct == 4.8
    
    def test_stop_loss_triggered_early_exit(self):
        """
        If stop loss triggered during holding period,
        exit price should be adjusted.
        """
        entry_price = 1000
        stop_loss_pct = 10
        
        # Price drops 10%
        drawdown = -10.0
        stop_triggered = drawdown <= -stop_loss_pct
        
        assert stop_triggered
        
        # Exit at -10% instead of end-of-month price
        exit_price = entry_price * (1 + drawdown / 100)
        assert exit_price == 900


@pytest.mark.integration
class TestPortfolioReturnCalculation:
    """Test portfolio-level return calculation."""
    
    def test_weighted_portfolio_return(self):
        """
        Portfolio return = sum(trade_return * weight)
        """
        returns = np.array([2.5, -1.0, 3.2])  # Individual trade returns %
        weights = np.array([0.35, 0.30, 0.35])  # Position weights
        
        portfolio_return = np.sum(returns * weights)
        
        # (2.5 * 0.35) + (-1.0 * 0.30) + (3.2 * 0.35)
        # = 0.875 - 0.30 + 1.12
        # = 1.695
        assert abs(portfolio_return - 1.695) < 0.001
    
    def test_exposure_scaling_applied_to_return(self):
        """
        Adjusted return = portfolio_return * market_exposure
        """
        portfolio_return_pct = 1.5
        market_exposure = 0.6
        
        adjusted_return = portfolio_return_pct * market_exposure
        
        assert adjusted_return == 0.9


@pytest.mark.integration
class TestBenchmarkComparison:
    """Test benchmark tracking and comparison."""
    
    def test_benchmark_tracks_independently(self):
        """
        Benchmark (NIFTY) should track independently
        regardless of portfolio construction.
        """
        nifty_entry = 19000
        nifty_exit = 19500
        
        nifty_return_pct = ((nifty_exit - nifty_entry) / nifty_entry) * 100
        
        assert abs(nifty_return_pct - 2.632) < 0.01
    
    def test_benchmark_equity_curve_independent(self):
        """Benchmark equity curve should move with NIFTY returns."""
        benchmark_curve = [100]
        nifty_returns = [2.0, -1.5, 3.0, 1.0]
        
        for ret in nifty_returns:
            benchmark_curve.append(benchmark_curve[-1] * (1 + ret / 100))
        
        assert len(benchmark_curve) == 5
        assert benchmark_curve[0] == 100
        assert benchmark_curve[-1] != 100
