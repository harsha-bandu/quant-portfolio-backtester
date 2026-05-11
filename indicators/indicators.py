import ta


def calculate_indicators(df):

    close = df['Close'].squeeze()
    volume = df['Volume'].squeeze()

    # 200 DMA
    df['DMA_200'] = (
        close
        .rolling(window=200)
        .mean()
    )

    # RSI
    rsi_indicator = ta.momentum.RSIIndicator(
        close=close,
        window=14
    )

    df['RSI'] = rsi_indicator.rsi()

    # 20-day average volume
    df['AVG_VOLUME_20'] = (
        volume
        .rolling(window=20)
        .mean()
    )

    df['Daily Return'] = (df['Close'].pct_change())

    df['Volatility'] = (df['Daily Return'].rolling(20).std())

    return df