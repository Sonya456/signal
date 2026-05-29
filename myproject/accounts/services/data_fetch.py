import requests
import pandas as pd
from django.core.cache import cache

BINANCE_KLINES_URL = "https://api.binance.com/api/v3/klines"



def fetch_klines_df(symbol: str, interval: str = "1h", limit: int = 200) -> pd.DataFrame:
    symbol = symbol.upper()
    cache_key = f"klines_{symbol}_{interval}_{limit}"

    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    data = requests.get(
        BINANCE_KLINES_URL,
        params={
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        },
        timeout=10
    ).json()

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

    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
    df["close_time"] = pd.to_datetime(df["close_time"], unit="ms")

    cache.set(cache_key, df, timeout=30)

    return df



def fetch_price(symbol):
    try:
        res = requests.get(
            "https://api.binance.com/api/v3/ticker/price",
            params={"symbol": symbol},
            timeout=10
        )

        data = res.json()

        if "price" not in data:
            raise ValueError("Invalid Binance response")

        return float(data["price"])

    except Exception as e:
        raise RuntimeError(f"Price fetch error: {str(e)}")