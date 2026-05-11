import yfinance as yf


def get_fundamentals(symbol):

    try:

        stock = yf.Ticker(symbol)

        info = stock.info

        fundamentals = {

            "PE Ratio": info.get("trailingPE"),
            "Market Cap": info.get("marketCap"),
            "ROE": info.get("returnOnEquity"),
            "Debt/Equity": info.get("debtToEquity"),
            "Revenue Growth": info.get("revenueGrowth")

        }

        return fundamentals

    except Exception as e:

        print(f"Fundamental error for {symbol}: {e}")

        return {
            "PE Ratio": None,
            "Market Cap": None,
            "ROE": None,
            "Debt/Equity": None,
            "Revenue Growth": None
        }