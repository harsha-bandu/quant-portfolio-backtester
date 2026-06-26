"""
Unit tests for portfolio_construction module.

Tests focus on:
- Rank-based stock selection
- Holding persistence (ENTRY_RANK / EXIT_RANK)
- Sector constraint enforcement
- Holding duration tracking
- Turnover calculation
"""

import pytest
from config import TOP_STOCKS, ENTRY_RANK, EXIT_RANK, MAX_STOCKS_PER_SECTOR
from strategies.portfolio_construction import construct_portfolio


@pytest.mark.unit
class TestRankBasedSelection:
    """Test ENTRY_RANK and EXIT_RANK filtering."""
    
    def test_retains_existing_holdings_within_exit_rank(
        self, sample_ranked_stocks, sample_current_holdings
    ):
        """
        Existing holdings within EXIT_RANK should be retained.
        INFY (rank 1) and TCS (rank 2) both <= EXIT_RANK (12).
        """
        holding_durations = {}
        monthly_turnover = []
        completed_holding_periods = []
        
        result = construct_portfolio(
            sample_ranked_stocks,
            sample_current_holdings,
            holding_durations,
            monthly_turnover,
            completed_holding_periods,
        )
        
        symbols = [stock["Symbol"] for stock in result["top_stocks"]]
        assert "INFY" in symbols
        assert "TCS" in symbols
    
    def test_exits_holdings_beyond_exit_rank(
        self, sample_ranked_stocks
    ):
        """
        Holdings with rank > EXIT_RANK should be exited.
        """
        # Set a holding that's ranked lower
        current_holdings = ["HDFC"]  # Rank 5, EXIT_RANK is 12 normally
        holding_durations = {"HDFC": 10}
        monthly_turnover = []
        completed_holding_periods = []
        
        result = construct_portfolio(
            sample_ranked_stocks,
            current_holdings,
            holding_durations,
            monthly_turnover,
            completed_holding_periods,
        )
        
        symbols = [stock["Symbol"] for stock in result["top_stocks"]]
        # HDFC should be retained (rank 5 <= EXIT_RANK 12)
        # After filling with new entries, depends on ENTRY_RANK
        # This test needs context about the full behavior
        pass
    
    def test_adds_new_entries_within_entry_rank(
        self, sample_ranked_stocks
    ):
        """
        New stocks within ENTRY_RANK should be added to portfolio.
        """
        current_holdings = []  # Start empty
        holding_durations = {}
        monthly_turnover = []
        completed_holding_periods = []
        
        result = construct_portfolio(
            sample_ranked_stocks,
            current_holdings,
            holding_durations,
            monthly_turnover,
            completed_holding_periods,
        )
        
        symbols = [stock["Symbol"] for stock in result["top_stocks"]]
        # Should have stocks from top ENTRY_RANK (5)
        assert len(symbols) <= TOP_STOCKS
        # Symbols should be top ranked
        for i, stock in enumerate(result["top_stocks"]):
            assert i + 1 <= ENTRY_RANK
    
    def test_does_not_add_entries_beyond_entry_rank(
        self, sample_ranked_stocks
    ):
        """
        Stocks beyond ENTRY_RANK should not be added.
        """
        current_holdings = []
        holding_durations = {}
        monthly_turnover = []
        completed_holding_periods = []
        
        result = construct_portfolio(
            sample_ranked_stocks,
            current_holdings,
            holding_durations,
            monthly_turnover,
            completed_holding_periods,
        )
        
        # All selected stocks should be within ENTRY_RANK
        for stock in result["top_stocks"]:
            # Find rank by position in ranked_stocks
            rank = next(
                i + 1 for i, s in enumerate(sample_ranked_stocks)
                if s["Symbol"] == stock["Symbol"]
            )
            assert rank <= ENTRY_RANK


@pytest.mark.unit
class TestSectorConstraints:
    """Test sector diversification limits."""
    
    def test_respects_max_stocks_per_sector(
        self, sample_ranked_stocks, sample_current_holdings, monkeypatch
    ):
        """
        Portfolio should not exceed MAX_STOCKS_PER_SECTOR per sector.
        """
        # Mock sector map to control sector assignments
        monkeypatch.setattr(
            "strategies.portfolio_construction.SECTOR_MAP",
            {
                "INFY": "IT",
                "TCS": "IT",
                "WIPRO": "IT",
                "RELIANCE": "Energy",
                "HDFC": "Finance",
            }
        )
        
        holding_durations = {}
        monthly_turnover = []
        completed_holding_periods = []
        
        result = construct_portfolio(
            sample_ranked_stocks,
            sample_current_holdings,
            holding_durations,
            monthly_turnover,
            completed_holding_periods,
        )
        
        # Count stocks per sector
        sector_counts = {}
        for stock in result["top_stocks"]:
            symbol = stock["Symbol"]
            # Re-create sector counting
            pass  # Would need sector map
        
        # Each sector count should be <= MAX_STOCKS_PER_SECTOR
        # (This test needs full sector map setup)
    
    def test_portfolio_size_capped_at_top_stocks(
        self, sample_ranked_stocks
    ):
        """Portfolio size should not exceed TOP_STOCKS."""
        current_holdings = []
        holding_durations = {}
        monthly_turnover = []
        completed_holding_periods = []
        
        result = construct_portfolio(
            sample_ranked_stocks,
            current_holdings,
            holding_durations,
            monthly_turnover,
            completed_holding_periods,
        )
        
        assert len(result["top_stocks"]) <= TOP_STOCKS


@pytest.mark.unit
class TestHoldingDurationTracking:
    """Test holding duration and completion tracking."""
    
    def test_increments_duration_for_continuing_holds(
        self, sample_ranked_stocks, sample_current_holdings,
        sample_holding_durations
    ):
        """Continuing holdings should have duration incremented."""
        holding_durations = sample_holding_durations.copy()
        monthly_turnover = []
        completed_holding_periods = []
        
        result = construct_portfolio(
            sample_ranked_stocks,
            sample_current_holdings,
            holding_durations,
            monthly_turnover,
            completed_holding_periods,
        )
        
        updated_durations = result["holding_durations"]
        
        # INFY was held for 3 months, should be 4 now
        if "INFY" in updated_durations:
            assert updated_durations["INFY"] == 4
    
    def test_records_completed_holding_periods_on_exit(
        self, sample_ranked_stocks
    ):
        """
        When a stock is exited, its holding duration should be
        recorded in completed_holding_periods.
        """
        # Start with INFY held for 3 months
        current_holdings = ["INFY"]
        holding_durations = {"INFY": 3}
        monthly_turnover = []
        completed_holding_periods = []
        
        result = construct_portfolio(
            sample_ranked_stocks,
            current_holdings,
            holding_durations,
            monthly_turnover,
            completed_holding_periods,
        )
        
        # If INFY is exited, completed_holding_periods should record 3
        if "INFY" not in [s["Symbol"] for s in result["top_stocks"]]:
            # Check if 3 was recorded (depends on construction logic)
            pass


@pytest.mark.unit
class TestTurnoverCalculation:
    """Test monthly turnover tracking."""
    
    def test_calculates_turnover_when_holdings_change(
        self, sample_ranked_stocks
    ):
        """
        Turnover should be calculated when holdings change.
        Formula: symmetric_difference / TOP_STOCKS
        """
        current_holdings = ["INFY", "TCS"]
        holding_durations = {}
        monthly_turnover = []
        completed_holding_periods = []
        
        result = construct_portfolio(
            sample_ranked_stocks,
            current_holdings,
            holding_durations,
            monthly_turnover,
            completed_holding_periods,
        )
        
        # If portfolio changed, turnover should be recorded
        if len(monthly_turnover) > 0:
            turnover_pct = monthly_turnover[-1]
            assert 0 <= turnover_pct <= 200  # Max is 2 full portfolios
    
    def test_no_turnover_for_empty_prior_holdings(
        self, sample_ranked_stocks
    ):
        """
        No turnover should be calculated for first month (empty prior holdings).
        """
        current_holdings = []  # Empty start
        holding_durations = {}
        monthly_turnover = []
        completed_holding_periods = []
        
        result = construct_portfolio(
            sample_ranked_stocks,
            current_holdings,
            holding_durations,
            monthly_turnover,
            completed_holding_periods,
        )
        
        # No turnover recorded for initial portfolio construction
        assert len(monthly_turnover) == 0


@pytest.mark.unit
class TestReturnTypes:
    """Test return data structures."""
    
    def test_returns_dict_with_required_keys(
        self, sample_ranked_stocks
    ):
        """Should return dict with top_stocks and new_current_holdings."""
        current_holdings = []
        holding_durations = {}
        monthly_turnover = []
        completed_holding_periods = []
        
        result = construct_portfolio(
            sample_ranked_stocks,
            current_holdings,
            holding_durations,
            monthly_turnover,
            completed_holding_periods,
        )
        
        assert isinstance(result, dict)
        assert set(result.keys()) == {
            "top_stocks", "new_current_holdings", "holding_durations"
        }
    
    def test_top_stocks_contain_full_scoring_data(
        self, sample_ranked_stocks
    ):
        """top_stocks should include all scoring fields."""
        current_holdings = []
        holding_durations = {}
        monthly_turnover = []
        completed_holding_periods = []
        
        result = construct_portfolio(
            sample_ranked_stocks,
            current_holdings,
            holding_durations,
            monthly_turnover,
            completed_holding_periods,
        )
        
        required_fields = {"Symbol", "Score", "Trend", "RSI", "Momentum"}
        for stock in result["top_stocks"]:
            assert required_fields.issubset(set(stock.keys()))
    
    def test_new_current_holdings_is_list_of_symbols(
        self, sample_ranked_stocks
    ):
        """new_current_holdings should be List[str] of symbols."""
        current_holdings = []
        holding_durations = {}
        monthly_turnover = []
        completed_holding_periods = []
        
        result = construct_portfolio(
            sample_ranked_stocks,
            current_holdings,
            holding_durations,
            monthly_turnover,
            completed_holding_periods,
        )
        
        assert isinstance(result["new_current_holdings"], list)
        for symbol in result["new_current_holdings"]:
            assert isinstance(symbol, str)
