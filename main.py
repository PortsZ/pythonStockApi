from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from lookup import lookup
from rebalance import rebalance
from uvicorn import run as uvicorn

app = FastAPI()

# ====================================================

@app.get("/")
def read_root():
    return {"Hello": "World"}

# ====================================================

@app.get("/lookup/{symbol}")
def read_item(symbol: str):
    return lookup(symbol)

# ====================================================

class StocksData(BaseModel):
    stocks: dict

@app.post("/rebalance")
async def rebalance_stocks(stocks_data: StocksData):
    stocks = stocks_data.stocks
    if not stocks:
        raise HTTPException(status_code=400, detail="No stocks data provided")

    rebalance_data = rebalance(stocks)
    return rebalance_data


if __name__ == "__main__":
    uvicorn("main:app", host="0.0.0.0", port=8000, reload=True)