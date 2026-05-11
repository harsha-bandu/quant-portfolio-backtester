import yfinance as yf
import plotly.graph_objects as go


def create_stock_chart(symbol):

    # Download data
    df = yf.download(
        symbol,
        period="1y",
        interval="1d",
        progress=False
    )

    if df.empty:
        return None

    # Flatten columns
    df.columns = df.columns.get_level_values(0)

    # 200 DMA
    df['DMA_200'] = (
        df['Close']
        .rolling(window=200)
        .mean()
    )

    # Create figure
    fig = go.Figure()

    # Candlestick
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Price'
        )
    )

    # 200 DMA
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['DMA_200'],
            mode='lines',
            name='200 DMA'
        )
    )

    # Layout
    fig.update_layout(
        title=f"{symbol} Price Chart",
        xaxis_title="Date",
        yaxis_title="Price",
        height=700,
        xaxis_rangeslider_visible=False
    )

    return fig