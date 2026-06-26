# =========================
# BACKTEST SETTINGS
# =========================

BACKTEST_YEARS = 5

STARTING_CAPITAL = 100

TOP_STOCKS = 5

# =========================
# RISK MANAGEMENT
# =========================

STOP_LOSS_PCT = 10

MAX_POSITION_WEIGHT = 0.30

RISK_FREE_RATE = 6

# =========================
# SCORING PARAMETERS
# =========================

RSI_WEIGHT = 25

TREND_WEIGHT = 12

RELATIVE_STRENGTH_WEIGHT = 4

VOLATILITY_PENALTY_WEIGHT = 4

# =========================
# LOOKBACK WINDOWS
# =========================

RSI_WINDOW = 14

VOLATILITY_WINDOW = 20

RELATIVE_STRENGTH_LOOKBACK = 126

# =========================
# TRANSACTION COSTS
# =========================

TRANSACTION_COST_PCT = 0.20

# ATR_STOP_MULTIPLIER = 4

HOLD_THRESHOLD_RANK = 10

MAX_STOCKS_PER_SECTOR = 2

# ==========================================
# HOLDING PERSISTENCE
# ==========================================

ENTRY_RANK = 5
EXIT_RANK = 12

# ==========================================
# MARKET BREADTH FILTER
# ==========================================

MIN_BREADTH_PCT = 50