from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes


import requests
import pandas as pd
from rest_framework.decorators import api_view
from rest_framework.response import Response



def get_trend_data(symbol):
    data = requests.get(
        "https://api.binance.com/api/v3/klines",
        params={"symbol": symbol, "interval": "1h", "limit": 200}
    ).json()

    df = pd.DataFrame(data, columns=[
        "open_time", "open", "high", "low", "close",
        "volume", "close_time", "qav", "trades",
        "tb_base", "tb_quote", "ignore"
    ])

    df["close"] = df["close"].astype(float)

    df["ema50"] = df["close"].ewm(span=50).mean()
    df["ema200"] = df["close"].ewm(span=200).mean()

    price = df["close"].iloc[-1]
    ema50 = df["ema50"].iloc[-1]
    ema200 = df["ema200"].iloc[-1]

    if price > ema200 and ema50 > ema200:
        return "bullish"
    elif price < ema200 and ema50 < ema200:
        return "bearish"
    else:
        return "neutral"



def get_rsi_data(symbol):
    data = requests.get(
        "https://api.binance.com/api/v3/klines",
        params={"symbol": symbol, "interval": "1h", "limit": 100}
    ).json()

    df = pd.DataFrame(data, columns=[
        "open_time", "open", "high", "low", "close",
        "volume", "close_time", "qav", "trades",
        "tb_base", "tb_quote", "ignore"
    ])

    df["close"] = df["close"].astype(float)

    delta = df["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    val = rsi.iloc[-1]

    if val < 30:
        return "oversold"
    elif val > 70:
        return "overbought"
    elif val < 40:
        return "weak"
    elif val > 60:
        return "strong"
    else:
        return "neutral"



def get_volume_data(symbol):
    data = requests.get(
        "https://api.binance.com/api/v3/klines",
        params={"symbol": symbol, "interval": "1h", "limit": 50}
    ).json()

    df = pd.DataFrame(data, columns=[
        "open_time", "open", "high", "low", "close",
        "volume", "close_time", "qav", "trades",
        "tb_base", "tb_quote", "ignore"
    ])

    df["volume"] = df["volume"].astype(float)

    current = df["volume"].iloc[-1]
    avg = df["volume"].rolling(20).mean().iloc[-1]

    ratio = current / avg

    if ratio > 2:
        return "spike"
    elif ratio > 1.3:
        return "increasing"
    elif ratio > 0.8:
        return "normal"
    else:
        return "low"


@api_view(['GET'])
def live_price(request):

    symbol = request.GET.get('symbol', 'BTCUSDT')

    res = requests.get(
        "https://api.binance.com/api/v3/ticker/price",
        params={"symbol": symbol}
    ).json()

    return Response({
        "symbol": symbol,
        "price": float(res["price"])
    })

@api_view(['GET'])
def resistance_distance(request):

    symbol = request.GET.get('symbol', 'BTCUSDT')

    url = "https://api.binance.com/api/v3/klines"

    params = {
        "symbol": symbol,
        "interval": "1h",
        "limit": 50
    }

    res = requests.get(url, params=params)
    data = res.json()

    df = pd.DataFrame(data, columns=[
        "open_time", "open", "high", "low", "close",
        "volume", "close_time", "qav", "trades",
        "tb_base", "tb_quote", "ignore"
    ])

    df["close"] = df["close"].astype(float)
    df["high"] = df["high"].astype(float)

    # ✅ resistance
    resistance = df["high"].rolling(20).max().iloc[-2]
    price = df["close"].iloc[-1]

    distance = (resistance - price) / price * 100  # %

    # ✅ LOGIC
    if distance < 0.5:
        status = "too_close"
        logic = "Price is too close to resistance, limited upside potential"

    elif distance < 2:
        status = "medium"
        logic = "Approaching resistance, moderate upside"

    else:
        status = "far"
        logic = "Enough room to resistance, potential move"

    return Response({
        "symbol": symbol,
        "distance": distance,
        "status": status,
        "logic": logic
    })




@api_view(['GET'])
def breakout_signal(request):

    symbol = request.GET.get('symbol', 'BTCUSDT')

    url = "https://api.binance.com/api/v3/klines"

    params = {
        "symbol": symbol,
        "interval": "1h",
        "limit": 50
    }

    res = requests.get(url, params=params)
    data = res.json()

    df = pd.DataFrame(data, columns=[
        "open_time", "open", "high", "low", "close",
        "volume", "close_time", "qav", "trades",
        "tb_base", "tb_quote", "ignore"
    ])

    df["close"] = df["close"].astype(float)
    df["high"] = df["high"].astype(float)

    # ✅ resistance
    resistance = df["high"].rolling(20).max().iloc[-2]

    last_close = df["close"].iloc[-1]

    # ✅ breakout condition → świeca zamyka się powyżej
    breakout = last_close > resistance

    # ✅ LOGIC
    if breakout:
        status = "confirmed"
        logic = "Candle closed above resistance level"

    else:
        status = "not_confirmed"
        logic = "No candle close above resistance level"

    return Response({
        "symbol": symbol,
        "price": last_close,
        "resistance": resistance,
        "status": status,
        "logic": logic
    })






@api_view(['GET'])
def support_reaction(request):

    symbol = request.GET.get('symbol', 'BTCUSDT')

    url = "https://api.binance.com/api/v3/klines"

    params = {
        "symbol": symbol,
        "interval": "1h",
        "limit": 50
    }

    res = requests.get(url, params=params)
    data = res.json()

    df = pd.DataFrame(data, columns=[
        "open_time", "open", "high", "low", "close",
        "volume", "close_time", "qav", "trades",
        "tb_base", "tb_quote", "ignore"
    ])

    df["close"] = df["close"].astype(float)
    df["low"] = df["low"].astype(float)
    df["open"] = df["open"].astype(float)

    # ✅ support level
    support = df["low"].rolling(20).min().iloc[-2]

    last_low = df["low"].iloc[-1]
    last_close = df["close"].iloc[-1]
    last_open = df["open"].iloc[-1]

    # ✅ czy dotknął supportu
    near_support = abs(last_low - support) / support < 0.002

    # ✅ strength candle
    bullish_candle = last_close > last_open
    bounce_strength = (last_close - last_low) / last_low

    # ✅ LOGIC
    if near_support and bullish_candle and bounce_strength > 0.01:
        status = "strong"
        logic = "Strong bullish bounce from support level"

    elif near_support:
        status = "weak"
        logic = "No strong bullish bounce from support"

    else:
        status = "none"
        logic = "Price not interacting with support"

    return Response({
        "symbol": symbol,
        "support": support,
        "price": last_close,
        "status": status,
        "logic": logic
    })



@api_view(['GET'])
def volume_signal(request):

    symbol = request.GET.get('symbol', 'BTCUSDT')

    url = "https://api.binance.com/api/v3/klines"

    params = {
        "symbol": symbol,
        "interval": "1h",
        "limit": 50
    }

    res = requests.get(url, params=params)
    data = res.json()

    df = pd.DataFrame(data, columns=[
        "open_time", "open", "high", "low", "close",
        "volume", "close_time", "qav", "trades",
        "tb_base", "tb_quote", "ignore"
    ])

    df["volume"] = df["volume"].astype(float)

    current_volume = df["volume"].iloc[-1]
    avg_volume = df["volume"].rolling(window=20).mean().iloc[-1]

    # ✅ ratio
    ratio = current_volume / avg_volume

    # ✅ LOGIC
    if ratio > 2:
        status = "spike"
        logic = "Strong volume spike, high activity"

    elif ratio > 1.3:
        status = "increasing"
        logic = "Above average volume, increasing interest"

    elif ratio > 0.8:
        status = "normal"
        logic = "Volume near average, no strong buying pressure"

    else:
        status = "low"
        logic = "Low volume, weak market participation"

    return Response({
        "symbol": symbol,
        "ratio": ratio,
        "status": status,
        "logic": logic
    })


@api_view(['GET'])
def market_structure(request):

    symbol = request.GET.get('symbol', 'BTCUSDT')

    url = "https://api.binance.com/api/v3/klines"

    params = {
        "symbol": symbol,
        "interval": "1h",
        "limit": 50
    }

    res = requests.get(url, params=params)
    data = res.json()

    df = pd.DataFrame(data, columns=[
        "open_time", "open", "high", "low", "close",
        "volume", "close_time", "qav", "trades",
        "tb_base", "tb_quote", "ignore"
    ])

    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)

    # ✅ ostatnie poziomy
    highs = df["high"].tail(5).values
    lows = df["low"].tail(5).values

    # ✅ sprawdzanie struktury
    higher_highs = all(x < y for x, y in zip(highs, highs[1:]))
    higher_lows = all(x < y for x, y in zip(lows, lows[1:]))

    lower_highs = all(x > y for x, y in zip(highs, highs[1:]))
    lower_lows = all(x > y for x, y in zip(lows, lows[1:]))

    # ✅ decyzja
    if higher_highs and higher_lows:
        structure = "strong_bull"
        logic = "Higher highs and higher lows detected"

    elif lower_highs and lower_lows:
        structure = "weak"
        logic = "Lower highs and lower lows detected"

    else:
        structure = "neutral"
        logic = "Mixed structure, no clear trend"

    return Response({
        "symbol": symbol,
        "structure": structure,
        "logic": logic
    })


@api_view(['GET'])
def rsi_signal(request):

    symbol = request.GET.get('symbol', 'BTCUSDT')

    url = "https://api.binance.com/api/v3/klines"

    params = {
        "symbol": symbol,
        "interval": "1h",
        "limit": 100
    }

    res = requests.get(url, params=params)
    data = res.json()

    df = pd.DataFrame(data, columns=[
        "open_time", "open", "high", "low", "close",
        "volume", "close_time", "qav", "trades",
        "tb_base", "tb_quote", "ignore"
    ])

    df["close"] = df["close"].astype(float)

    # ✅ RSI CALCULATION
    delta = df["close"].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss
    df["rsi"] = 100 - (100 / (1 + rs))

    rsi = df["rsi"].iloc[-1]

    # ✅ LOGIKA
    if rsi < 30:
        status = "oversold"
        logic = "Strong oversold conditions, potential bounce"

    elif rsi > 70:
        status = "overbought"
        logic = "Overbought, possible reversal"

    elif rsi < 40:
        status = "weak"
        logic = "Weak momentum, but not yet oversold"

    elif rsi > 60:
        status = "strong"
        logic = "Strong bullish momentum"

    else:
        status = "neutral"
        logic = "No clear momentum"

    return Response({
        "symbol": symbol,
        "rsi": float(rsi),
        "status": status,
        "logic": logic
    })

@api_view(['GET'])
def trend_filter(request):

    symbol = request.GET.get('symbol', 'BTCUSDT')

    url = "https://api.binance.com/api/v3/klines"

    params = {
        "symbol": symbol,
        "interval": "1h",
        "limit": 200
    }

    res = requests.get(url, params=params)
    data = res.json()

    df = pd.DataFrame(data, columns=[
        "open_time", "open", "high", "low", "close",
        "volume", "close_time", "qav", "trades",
        "tb_base", "tb_quote", "ignore"
    ])

    df["close"] = df["close"].astype(float)

    # ✅ EMA
    df["ema50"] = df["close"].ewm(span=50).mean()
    df["ema200"] = df["close"].ewm(span=200).mean()

    price = df["close"].iloc[-1]
    ema50 = df["ema50"].iloc[-1]
    ema200 = df["ema200"].iloc[-1]

    # ✅ LOGIKA
    if price > ema200 and ema50 > ema200:
        trend = "bullish"
        logic = "Price above EMA200 and EMA50 above EMA200"

    elif price < ema200 and ema50 < ema200:
        trend = "bearish"
        logic = "Price below EMA200 and EMA50 below EMA200"

    else:
        trend = "neutral"
        logic = "Mixed trend (no clear direction)"

    return Response({
        "symbol": symbol,
        "price": price,
        "trend": trend,
        "logic": logic
    })



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_api(request):
    return Response({
        'message': f'Hello {request.user.username}'
    })

def home(request):
    return render(request, 'accounts/home.html')



@api_view(['POST'])
def register_api(request):

    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    if not username or not email or not password:
        return Response({
            'error': 'All fields are required'
        }, status=400)

    if User.objects.filter(username=username).exists():
        return Response({
            'error': 'Username already exists'
        }, status=400)

    if User.objects.filter(email=email).exists():
        return Response({
            'error': 'Email already exists'
        }, status=400)

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )

    refresh = RefreshToken.for_user(user)

    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    })


@api_view(['GET'])
def protected_api(request):
    return Response({
        'message': 'JWT działa ✅'
    })

# LOGIN (JWT)
@api_view(['POST'])
@permission_classes([AllowAny])
def login_api(request):
    username = request.data.get('username')
    password = request.data.get('password')

    from django.contrib.auth import authenticate

    user = authenticate(username=username, password=password)

    if user is None:
        return Response({"error": "Invalid credentials"}, status=401)

    refresh = RefreshToken.for_user(user)

    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    })


#  LOGOUT (blacklist)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_api(request):
    try:
        refresh_token = request.data.get("refresh")
        token = RefreshToken(refresh_token)
        token.blacklist()

        return Response({"message": "Logged out"}, status=200)
    except Exception:
        return Response({"error": "Invalid token"}, status=400)




@api_view(['GET'])
def long_score(request):

    symbol = request.GET.get('symbol', 'BTCUSDT')

    # ✅ używamy funkcji helperów
    trend = get_trend_data(symbol)
    rsi = get_rsi_data(symbol)
    volume = get_volume_data(symbol)

    score = 0
    reasons = []

    # ✅ TREND
    if trend == "bullish":
        score += 2
        reasons.append("Trend supports long")

    # ✅ RSI
    if rsi in ["oversold", "strong"]:
        score += 1
        reasons.append("Momentum supports upside")

    # ✅ VOLUME
    if volume in ["spike", "increasing"]:
        score += 1
        reasons.append("Volume confirms interest")

    return Response({
        "symbol": symbol,
        "score": score,
        "max_score": 10,
        "probability": "HIGH" if score >= 7 else "MEDIUM" if score >= 4 else "LOW",
        "reasons": reasons
    })


from django.shortcuts import render


# FRONTEND PAGES

def home(request):
    return render(request, 'accounts/home.html')


def frontend_login(request):
    return render(request, 'accounts/login.html')


def frontend_register(request):
    return render(request, 'accounts/register.html')


def profile_page(request):
    return render(request, 'accounts/profile.html')