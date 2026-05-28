from .data_fetch import fetch_klines_df


def compute_distance(df):
    resistance = df["high"].rolling(20).max().iloc[-2]
    price = df["close"].iloc[-1]

    distance = (resistance - price) / price * 100

    if distance < 0.5:
        return "too_close", distance
    elif distance < 2:
        return "medium", distance
    return "far", distance









def compute_support(df):
    support = df["low"].rolling(20).min().iloc[-2]

    last_low = df["low"].iloc[-1]
    last_open = df["open"].iloc[-1]
    last_close = df["close"].iloc[-1]

    near = abs(last_low - support) / support < 0.002
    bullish = last_close > last_open
    strength = (last_close - last_low) / last_low

    if near and bullish and strength > 0.01:
        status = "strong"
    elif near:
        status = "weak"
    else:
        status = "none"

    return {
        "status": status,
        "support": support
    }



def compute_breakout(df):
    resistance = df["high"].rolling(20).max().iloc[-2]
    price = df["close"].iloc[-1]

    return "confirmed" if price > resistance else "not_confirmed", resistance

def get_structure_status(symbol: str) -> str:
    df = fetch_klines_df(symbol, limit=60)
    highs = df["high"].tail(5).values
    lows = df["low"].tail(5).values

    higher_highs = all(x < y for x, y in zip(highs, highs[1:]))
    higher_lows = all(x < y for x, y in zip(lows, lows[1:]))

    lower_highs = all(x > y for x, y in zip(highs, highs[1:]))
    lower_lows = all(x > y for x, y in zip(lows, lows[1:]))

    if higher_highs and higher_lows:
        return "strong_bull"
    if lower_highs and lower_lows:
        return "weak"
    return "neutral"


def get_breakout_status(symbol: str) -> str:
    df = fetch_klines_df(symbol, limit=60)
    resistance = df["high"].rolling(20).max().iloc[-2]
    last_close = df["close"].iloc[-1]

    return "confirmed" if last_close > resistance else "not_confirmed"


def get_distance_status(symbol: str) -> str:
    df = fetch_klines_df(symbol, limit=60)
    resistance = df["high"].rolling(20).max().iloc[-2]
    price = df["close"].iloc[-1]

    distance_pct = (resistance - price) / price * 100

    if distance_pct < 0.5:
        return "too_close"
    if distance_pct < 2:
        return "medium"
    return "far"


def get_support_status(symbol: str) -> str:
    df = fetch_klines_df(symbol, limit=60)
    support = df["low"].rolling(20).min().iloc[-2]

    last_low = df["low"].iloc[-1]
    last_open = df["open"].iloc[-1]
    last_close = df["close"].iloc[-1]

    near_support = abs(last_low - support) / support < 0.002
    bullish_candle = last_close > last_open
    bounce_strength = (last_close - last_low) / last_low

    if near_support and bullish_candle and bounce_strength > 0.01:
        return "strong"
    if near_support:
        return "weak"
    return "none"


def compute_structure(df):
    highs = df["high"].tail(5).values
    lows = df["low"].tail(5).values

    higher_highs = all(x < y for x, y in zip(highs, highs[1:]))
    higher_lows = all(x < y for x, y in zip(lows, lows[1:]))

    lower_highs = all(x > y for x, y in zip(highs, highs[1:]))
    lower_lows = all(x > y for x, y in zip(lows, lows[1:]))

    if higher_highs and higher_lows:
        return {
            "structure": "strong_bull",
            "logic": "Higher highs + higher lows"
        }
    elif lower_highs and lower_lows:
        return {
            "structure": "weak",
            "logic": "Lower highs + lower lows"
        }
    else:
        return {
            "structure": "neutral",
            "logic": "Mixed structure"
        }




