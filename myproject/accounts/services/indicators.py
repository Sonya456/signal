import pandas as pd





# def get_rsi_data(symbol):
#     data = requests.get(
#         "https://api.binance.com/api/v3/klines",
#         params={"symbol": symbol, "interval": "1h", "limit": 100}
#     ).json()
#
#     df = pd.DataFrame(data, columns=[
#         "open_time", "open", "high", "low", "close",
#         "volume", "close_time", "qav", "trades",
#         "tb_base", "tb_quote", "ignore"
#     ])
#
#     df["close"] = df["close"].astype(float)
#
#     delta = df["close"].diff()
#     gain = delta.clip(lower=0)
#     loss = -delta.clip(upper=0)
#
#     avg_gain = gain.rolling(14).mean()
#     avg_loss = loss.rolling(14).mean(
#
#     rs = avg_gain / avg_loss
#     rsi = 100 - (100 / (1 + rs))
#
#     val = rsi.iloc[-1]
#
#     if val < 30:
#         return "oversold"
#     elif val > 70:
#         return "overbought"
#     elif val < 40:
#         return "weak"
#     elif val > 60:
#         return "strong"
#     else:
#         return "neutral"



# def get_volume_data(symbol):
#     data = requests.get(
#         "https://api.binance.com/api/v3/klines",
#         params={"symbol": symbol, "interval": "1h", "limit": 50}
#     ).json()
#
#     df = pd.DataFrame(data, columns=[
#         "open_time", "open", "high", "low", "close",
#         "volume", "close_time", "qav", "trades",
#         "tb_base", "tb_quote", "ignore"
#     ])
#
#     df["volume"] = df["volume"].astype(float)
#
#     current = df["volume"].iloc[-1]
#     avg = df["volume"].rolling(20).mean().iloc[-1]
#
#     ratio = current / avg
#
#     if ratio > 2:
#         return "spike"
#     elif ratio > 1.3:
#         return "increasing"
#     elif ratio > 0.8:
#         return "normal"
#     else:
#         return "low"
#
#



def compute_volume(df):
    current_volume = df["volume"].iloc[-1]
    avg_volume = df["volume"].rolling(window=20).mean().iloc[-1]

    ratio = current_volume / avg_volume

    if ratio > 2:
        status = "spike"
        logic = "Strong volume spike"
    elif ratio > 1.3:
        status = "increasing"
        logic = "Above average volume"
    elif ratio > 0.8:
        status = "normal"
        logic = "Volume near average"
    else:
        status = "low"
        logic = "Low market participation"

    return {
        "ratio": ratio,
        "status": status,
        "logic": logic
    }


def compute_trend(df):
    df["ema50"] = df["close"].ewm(span=50).mean()
    df["ema200"] = df["close"].ewm(span=200).mean()

    price = df["close"].iloc[-1]
    ema50 = df["ema50"].iloc[-1]
    ema200 = df["ema200"].iloc[-1]

    if price > ema200 and ema50 > ema200:
        trend = "bullish"
        logic = "Above EMA200"
    elif price < ema200 and ema50 < ema200:
        trend = "bearish"
        logic = "Below EMA200"
    else:
        trend = "neutral"
        logic = "Mixed trend"

    return {
        "trend": trend,
        "price": price,
        "logic": logic
    }


def compute_rsi(df):
    # RSI CALCULATION
    delta = df["close"].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss
    rsi_series = 100 - (100 / (1 + rs))

    rsi = rsi_series.iloc[-1]

    # LOGIC
    if rsi < 30:
        status = "oversold"
        logic = "Strong oversold conditions, potential bounce"
    elif rsi > 70:
        status = "overbought"
        logic = "Overbought, possible reversal"
    elif rsi < 40:
        status = "weak"
        logic = "Weak momentum"
    elif rsi > 60:
        status = "strong"
        logic = "Strong bullish momentum"
    else:
        status = "neutral"
        logic = "No clear momentum"

    return {
        "rsi": float(rsi),
        "status": status,
        "logic": logic
    }
