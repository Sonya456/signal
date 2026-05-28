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
from .services.scoring import calculate_score
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
    symbol = request.GET.get("symbol", "BTCUSDT").upper()

    try:
        df = fetch_klines_df(symbol, limit=200)

        signals = {
            "trend": compute_trend(df)["trend"],
            "rsi": compute_rsi(df)["status"],
            "volume": compute_volume(df)["status"],
            "structure": compute_structure(df)["structure"],
            "breakout": compute_breakout(df)["status"],
            "distance": compute_distance(df)["status"],
            "support": compute_support(df)["status"],
        }

        score, reasons = calculate_score(signals)

        probability = (
            "HIGH" if score >= 7 else
            "MEDIUM" if score >= 4 else
            "LOW"
        )

        return Response({
            "symbol": symbol,
            "score": score,
            "probability": probability,
            "signals": signals,
            "reasons": reasons
        })

    except Exception as e:
        return Response({"error": str(e)}, status=500)


# FRONTEND PAGES

def home(request):
    return render(request, 'accounts/home.html')


def frontend_login(request):
    return render(request, 'accounts/login.html')


def frontend_register(request):
    return render(request, 'accounts/register.html')


def profile_page(request):
    return render(request, 'accounts/profile.html')