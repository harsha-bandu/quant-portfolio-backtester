from config import (
    TOP_STOCKS,
    ENTRY_RANK,
    EXIT_RANK,
    MAX_STOCKS_PER_SECTOR,
)
from universe.sector_map import SECTOR_MAP

"""
Portfolio Construction Engine

Responsible for:
- Rank-based stock selection (ENTRY_RANK / EXIT_RANK)
- Holding persistence logic
- Sector constraint enforcement
- Holding duration tracking
- Turnover calculation

This module contains no scoring, factor calculation, or trade simulation logic.
"""


# =====================================================
# PORTFOLIO CONSTRUCTION
# =====================================================

def construct_portfolio(
    ranked_stocks,
    current_holdings,
    holding_durations,
    monthly_turnover,
    completed_holding_periods,
):
    """
    Construct portfolio from ranked stocks applying rank-based selection,
    sector constraints, and holding persistence.

    Args:
        ranked_stocks: List of scored stocks from score_universe(),
                      sorted by composite score (highest first)
        current_holdings: List of currently held stock symbols
        holding_durations: Dict mapping symbol to holding duration in months
        monthly_turnover: List to accumulate monthly turnover percentages
        completed_holding_periods: List to accumulate completed holding durations

    Returns:
        Dict with keys:
        - top_stocks: List of selected stock dicts with full scoring info
        - new_current_holdings: List of selected stock symbols for next period
        - holding_durations: Updated dict tracking holding durations
    """

    # =====================================================
    # RANK MAP
    # =====================================================

    rank_map = {}

    for idx, stock in enumerate(ranked_stocks):
        rank_map[stock["Symbol"]] = idx + 1

    # =====================================================
    # KEEP EXISTING HOLDINGS
    # =====================================================

    new_holdings = []

    for stock in ranked_stocks:

        symbol = stock["Symbol"]

        if symbol in current_holdings:

            if rank_map[symbol] <= EXIT_RANK:

                new_holdings.append(stock)

    # =====================================================
    # ADD NEW ENTRIES
    # =====================================================

    for stock in ranked_stocks:

        symbol = stock["Symbol"]

        if len(new_holdings) >= TOP_STOCKS:
            break

        already_exists = any(
            x["Symbol"] == symbol
            for x in new_holdings
        )

        if already_exists:
            continue

        if rank_map[symbol] <= ENTRY_RANK:

            new_holdings.append(stock)

    # =====================================================
    # APPLY SECTOR CONSTRAINTS
    # =====================================================

    sector_counts = {}

    filtered_holdings = []

    for stock in new_holdings:

        symbol = stock["Symbol"]

        sector = SECTOR_MAP.get(
            symbol,
            "Unknown"
        )

        current_sector_count = (
            sector_counts.get(sector, 0)
        )

        if (
            current_sector_count
            < MAX_STOCKS_PER_SECTOR
        ):

            filtered_holdings.append(stock)

            sector_counts[sector] = (
                current_sector_count + 1
            )

        if len(filtered_holdings) >= TOP_STOCKS:
            break

    top_stocks = filtered_holdings

    new_current_holdings = [
        x["Symbol"]
        for x in top_stocks
    ]

    # =====================================================
    # TURNOVER CALCULATION
    # =====================================================

    if len(current_holdings) > 0:

        old_set = set(current_holdings)

        new_set = set(new_current_holdings)

        turnover_count = len(
            old_set.symmetric_difference(new_set)
        )

        turnover_pct = (
            turnover_count
            / max(TOP_STOCKS, 1)
        ) * 100

        monthly_turnover.append(
            round(turnover_pct, 2)
        )

    # =====================================================
    # HOLDING DURATION TRACKING
    # =====================================================

    for symbol in new_current_holdings:

        if symbol in holding_durations:

            holding_durations[symbol] += 1

        else:

            holding_durations[symbol] = 1

    for symbol in current_holdings:

        if symbol not in new_current_holdings:

            completed_holding_periods.append(
                holding_durations[symbol]
            )

            del holding_durations[symbol]

    return {
        "top_stocks": top_stocks,
        "new_current_holdings": new_current_holdings,
        "holding_durations": holding_durations,
    }
