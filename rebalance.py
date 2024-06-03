import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import pytz

def rebalance(stocks):

    # Categorize each stock into its asset class
    asset_classes = {"stocks": [], "reits": []}
    for stock in stocks:
        if stock[4:-3] == "11":  # MXRF11.SA
            asset_classes["reits"].append(stock)
        else:
            asset_classes["stocks"].append(stock)

    # Adjust asset class weights based on presence of REITs
    if not asset_classes["reits"]:
        asset_class_weights = {"stocks": 1.0, "reits": 0.0}
    else:
        asset_class_weights = {"stocks": 0.5, "reits": 0.5}

    # Print to verify the classification
    # print("Stocks classified as REITs:", asset_classes["reits"])
    end = datetime.datetime.now(pytz.timezone("US/Eastern"))

    # Fetch historical data and dividends for these stocks
    data = yf.download(list(stocks.keys()), start="2020-01-01", end=end)['Adj Close']
    dividends = {stock: yf.Ticker(stock).dividends for stock in stocks}
    annual_dividend_yield = {stock: dividends[stock].sum() / data[stock].mean() for stock in stocks}

    # Calculate the latest price for each stock
    latest_prices = data.iloc[-1]

    # Calculate the total market value of the portfolio
    market_values = latest_prices * pd.Series(stocks)
    total_market_value = market_values.sum()
    # print("\n\n\n\nTotal Market Value of Portfolio: ", total_market_value)

    # Assuming a risk-free rate of 4%
    risk_free_rate = 0.04

    # Function to calculate Sharpe Ratio including dividends
    def calculate_sharpe_ratio(asset):
        daily_returns = data[asset].pct_change().dropna()
        annual_returns = daily_returns.mean() * 252
        adjusted_annual_returns = annual_returns + annual_dividend_yield[asset]
        volatility = daily_returns.std() * np.sqrt(252) #risk
        sharpe_ratio = (adjusted_annual_returns - risk_free_rate) / volatility
        return max(sharpe_ratio, 0)  # Set negative Sharpe Ratios to 0

    # Calculate Sharpe Ratios for all assets
    sharpe_ratios = {stock: calculate_sharpe_ratio(stock) for stock in stocks}

    # Normalize Sharpe Ratios only for stocks
    total_sharpe = sum(sharpe_ratios[stock] for stock in asset_classes["stocks"])
    normalized_sharpe = {}
    if total_sharpe > 0:
        normalized_sharpe = {stock: sharpe_ratios[stock] / total_sharpe for stock in asset_classes["stocks"]}


    # Allocate to stocks based on Sharpe Ratios
    allocated_stocks = {}
    if asset_classes["stocks"]:
        allocated_stocks = {stock: round(total_market_value * asset_class_weights["stocks"] * normalized_sharpe.get(stock, 0) / latest_prices[stock]) for stock in asset_classes["stocks"]}

    # Calculate total market value of REITs
    total_reits_market_value = sum(market_values[reit] for reit in asset_classes["reits"])
    # print("\n\n\n\nTotal REITs Market Value: ", total_reits_market_value)

    # Allocate to REITs evenly
    allocated_reits = {}
    if asset_classes["reits"]:
        reits_allocation_per_asset = round(total_market_value * asset_class_weights["reits"] / len(asset_classes["reits"]))
        allocated_reits = {reit: round(reits_allocation_per_asset / latest_prices[reit]) for reit in asset_classes["reits"]}

    # Combine the allocations
    final_allocation = {**allocated_stocks, **allocated_reits}

    # Recalculate adjusted market values with rounded quantities
    adjusted_market_values = {asset: final_allocation[asset] * latest_prices[asset] for asset in final_allocation}


    # Create DataFrame for stocks, adjusted quantities, and weights
    portfolio_df = pd.DataFrame(index=stocks.keys())
    portfolio_df['Adjusted Quantities'] = pd.Series(final_allocation)
    portfolio_df['Adjusted Market Values'] = portfolio_df['Adjusted Quantities'] * latest_prices
    portfolio_df['Sharpe Ratios'] = pd.Series(sharpe_ratios).fillna("N/A")  # Include Sharpe Ratios for all



    # Apply rounding to Adjusted Market Values in the DataFrame
    portfolio_df['Adjusted Market Values'] = portfolio_df['Adjusted Market Values'].round(2)



    # Recalculate the total adjusted market value of the portfolio
    total_adjusted_market_value = round(portfolio_df['Adjusted Market Values'].sum(), 2)
    portfolio_df['Weights'] = portfolio_df['Adjusted Market Values'] / total_adjusted_market_value

    portfolio_df["Weights"] = portfolio_df ["Weights"].round(2)




    # Output the results
    # print("\n\n\n\n\n", portfolio_df)
    # print("\n\n\n\nTotal Adjusted Market Value of Portfolio: ", total_adjusted_market_value)
    # print("\n\n\n\n")

    #return portfolio_df and total_adjusted_market_value
    # Convert DataFrame to a dictionary for JSON response
    result = {
        "portfolio": portfolio_df.to_dict(),
        "total_adjusted_market_value": total_adjusted_market_value
    }
    return result
