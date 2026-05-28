import requests
import pandas as pd

BINANCE_KLINES_URL = "https://api.binance.com/api/v3/klines"

def fetch_klines_df(symbol: str, interval: str = "1h", limit: int = 60) -> pd.DataFrame:
    data = requests.get(
        BINANCE_KLINES_URL,
        params={"symbol": symbol, "interval": interval, "limit": limit},
        timeout=10,
    ).json()

    # Binance w przypadku błędu zwraca dict z 'code'/'msg'
    if isinstance(data, dict) and "code" in data:
        raise RuntimeError(f"Binance error: {data.get('msg')}")

    df = pd.DataFrame(data, columns=[
        "open_time", "open", "high", "low", "close",
        "volume", "close_time", "qav", "trades",
        "tb_base", "tb_quote", "ignore"
    ])

    df["open"] = df["open"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["close"] = df["close"].astype(float)
    df["volume"] = df["volume"].astype(float)

    return df



def fetch_price(symbol):
    res = requests.get(
        "https://api.binance.com/api/v3/ticker/price",
        params={"symbol": symbol},
        timeout=10
    )

    data = res.json()

    return float(data["price"])
