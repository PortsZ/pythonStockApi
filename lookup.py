
import datetime
import pytz
import yfinance as yf



def lookup(symbol):
    """Look up quote for symbol."""

    # Prepare API request
    symbol = symbol.upper()
    end = datetime.datetime.now(pytz.timezone("US/Eastern"))
    start = end - datetime.timedelta(days=7)
    
    
    try:
        # Fetch historical data
        data = yf.download(symbol, start=start.date(), end=end.date(), interval="1d")
        
        if data.empty:
            print(f"No data found for symbol: {symbol}")
            return None

        # Get the most recent adjusted closing price
        latest_quote = data.iloc[-1]
        price = round(latest_quote['Adj Close'], 2)

        
        return {"name": symbol, "price": price, "symbol": symbol}
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None