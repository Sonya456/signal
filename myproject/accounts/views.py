# Django
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

# DRF
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status as drf_status

# JWT
from rest_framework_simplejwt.tokens import RefreshToken

# Services (twoja logika)
from .services.data_fetch import fetch_price, fetch_klines_df
from .services.indicators import compute_rsi, compute_trend, compute_volume
from .services.signals import (
    compute_structure,
    compute_breakout,
    compute_distance,
    compute_support
)





@api_view(['GET'])
def live_price(request):
    symbol = request.GET.get('symbol', 'BTCUSDT')

    price = fetch_price(symbol)

    return Response({
        "symbol": symbol,
        "price": price
    })



@api_view(['GET'])
def resistance_distance(request):
    symbol = request.GET.get('symbol', 'BTCUSDT')

    df = fetch_klines_df(symbol)

    status, distance = compute_distance(df)

    return Response({
        "symbol": symbol,
        "distance": distance,
        "status": status
    })





@api_view(['GET'])
def breakout_signal(request):
    symbol = request.GET.get('symbol', 'BTCUSDT')

    df = fetch_klines_df(symbol)

    status, resistance = compute_breakout(df)

    return Response({
        "symbol": symbol,
        "status": status,
        "resistance": resistance
    })




@api_view(['GET'])
def support_reaction(request):
    symbol = request.GET.get('symbol', 'BTCUSDT')

    df = fetch_klines_df(symbol)

    status, support = compute_support(df)

    return Response({
        "symbol": symbol,
        "support": support,
        "status": status
    })


@api_view(['GET'])
def rsi_signal(request):
    symbol = request.GET.get('symbol', 'BTCUSDT')

    df = fetch_klines_df(symbol, limit=100)

    result = compute_rsi(df)

    return Response({
        "symbol": symbol,
        **result
    })



@api_view(['GET'])
def volume_signal(request):
    symbol = request.GET.get('symbol', 'BTCUSDT')

    df = fetch_klines_df(symbol, limit=50)

    result = compute_volume(df)

    return Response({
        "symbol": symbol,
        **result
    })




@api_view(['GET'])
def market_structure(request):
    symbol = request.GET.get('symbol', 'BTCUSDT')

    df = fetch_klines_df(symbol, limit=50)

    result = compute_structure(df)

    return Response({
        "symbol": symbol,
        **result
    })



@api_view(['GET'])
def trend_filter(request):
    symbol = request.GET.get('symbol', 'BTCUSDT')

    df = fetch_klines_df(symbol, limit=200)

    result = compute_trend(df)

    return Response({
        "symbol": symbol,
        **result
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







@api_view(["GET"])
def long_score(request):
    symbol = request.GET.get("symbol", "BTCUSDT")

    try:

        df = fetch_klines_df(symbol, limit=200)

        # ===== COMPUTE ALL SIGNALS =====

        # 🔹 TREND (EMA)
        df["ema50"] = df["close"].ewm(span=50).mean()
        df["ema200"] = df["close"].ewm(span=200).mean()

        price = df["close"].iloc[-1]
        ema50 = df["ema50"].iloc[-1]
        ema200 = df["ema200"].iloc[-1]

        if price > ema200 and ema50 > ema200:
            trend = "bullish"
        elif price < ema200 and ema50 < ema200:
            trend = "bearish"
        else:
            trend = "neutral"

        # 🔹 RSI
        delta = df["close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()

        rs = avg_gain / avg_loss
        rsi_val = (100 - (100 / (1 + rs))).iloc[-1]

        if rsi_val < 30:
            rsi = "oversold"
        elif rsi_val > 70:
            rsi = "overbought"
        elif rsi_val < 40:
            rsi = "weak"
        elif rsi_val > 60:
            rsi = "strong"
        else:
            rsi = "neutral"

        # 🔹 VOLUME
        vol_current = df["volume"].iloc[-1]
        vol_avg = df["volume"].rolling(20).mean().iloc[-1]
        vol_ratio = vol_current / vol_avg

        if vol_ratio > 2:
            volume = "spike"
        elif vol_ratio > 1.3:
            volume = "increasing"
        elif vol_ratio > 0.8:
            volume = "normal"
        else:
            volume = "low"

        # 🔹 STRUCTURE
        highs = df["high"].tail(5).values
        lows = df["low"].tail(5).values

        higher_highs = all(x < y for x, y in zip(highs, highs[1:]))
        higher_lows = all(x < y for x, y in zip(lows, lows[1:]))

        lower_highs = all(x > y for x, y in zip(highs, highs[1:]))
        lower_lows = all(x > y for x, y in zip(lows, lows[1:]))

        if higher_highs and higher_lows:
            structure = "strong_bull"
        elif lower_highs and lower_lows:
            structure = "weak"
        else:
            structure = "neutral"

        # 🔹 BREAKOUT
        resistance = df["high"].rolling(20).max().iloc[-2]
        breakout = "confirmed" if price > resistance else "not_confirmed"

        # 🔹 DISTANCE
        distance_pct = (resistance - price) / price * 100

        if distance_pct < 0.5:
            distance = "too_close"
        elif distance_pct < 2:
            distance = "medium"
        else:
            distance = "far"

        # 🔹 SUPPORT
        support_lvl = df["low"].rolling(20).min().iloc[-2]

        last_low = df["low"].iloc[-1]
        last_open = df["open"].iloc[-1]
        last_close = df["close"].iloc[-1]

        near_support = abs(last_low - support_lvl) / support_lvl < 0.002
        bullish_candle = last_close > last_open
        bounce_strength = (last_close - last_low) / last_low

        if near_support and bullish_candle and bounce_strength > 0.01:
            support = "strong"
        elif near_support:
            support = "weak"
        else:
            support = "none"

    except Exception as e:
        return Response(
            {"error": str(e), "symbol": symbol},
            status=drf_status.HTTP_503_SERVICE_UNAVAILABLE
        )

    # ===== SCORING =====

    score = 0
    reasons = []

    # Trend
    if trend == "bullish":
        score += 2
        reasons.append("Trend bullish (+2)")
    elif trend == "neutral":
        score += 1
        reasons.append("Trend neutral (+1)")
    else:
        reasons.append("Trend bearish (+0)")

    # Structure
    if structure == "strong_bull":
        score += 2
        reasons.append("Structure HH+HL (+2)")
    elif structure == "neutral":
        score += 1
        reasons.append("Structure mixed (+1)")
    else:
        reasons.append("Structure weak (+0)")

    # Breakout
    if breakout == "confirmed":
        score += 2
        reasons.append("Breakout confirmed (+2)")
    else:
        reasons.append("No breakout (+0)")

    # Distance
    if distance == "far":
        score += 1
        reasons.append("Room to resistance (+1)")
    else:
        reasons.append("Too close to resistance (+0)")

    # Support
    if support == "strong":
        score += 1
        reasons.append("Strong support bounce (+1)")
    else:
        reasons.append("No strong support (+0)")

    # RSI
    if rsi in ["oversold", "strong"]:
        score += 1
        reasons.append("RSI supports (+1)")
    else:
        reasons.append("RSI not supporting (+0)")

    # Volume
    if volume in ["spike", "increasing"]:
        score += 1
        reasons.append("Volume supports (+1)")
    else:
        reasons.append("Volume weak/normal (+0)")

    # ===== FINAL RESULT =====

    if score >= 7:
        probability = "HIGH"
    elif score >= 4:
        probability = "MEDIUM"
    else:
        probability = "LOW"

    long_alarm = (
        score >= 7 and
        trend != "bearish" and
        (breakout == "confirmed" or support == "strong")
    )

    return Response({
        "symbol": symbol,
        "score": score,
        "max_score": 10,
        "probability": probability,
        "long_alarm": long_alarm,

        "signals": {
            "trend": trend,
            "structure": structure,
            "breakout": breakout,
            "distance": distance,
            "support": support,
            "rsi": rsi,
            "volume": volume,
        },
        "reasons": reasons,
    })


# FRONTEND PAGES

def home(request):
    return render(request, 'accounts/home.html')


def frontend_login(request):
    return render(request, 'accounts/login.html')


def frontend_register(request):
    return render(request, 'accounts/register.html')


def profile_page(request):
    return render(request, 'accounts/profile.html')