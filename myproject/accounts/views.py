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


@api_view(['GET'])
def trend_filter(request):

    symbol = request.GET.get('symbol', 'BTCUSDT')

    url = "https://api.binance.com/api/v3/klines"

    params = {
        "symbol": symbol,
        "interval": "1h",
        "limit": 200
    }

    response = requests.get(url, params=params)
    data = response.json()

    # zamiana na dataframe
    df = pd.DataFrame(data, columns=[
        "open_time", "open", "high", "low", "close",
        "volume", "close_time", "quote_asset_volume",
        "number_of_trades", "taker_buy_base",
        "taker_buy_quote", "ignore"
    ])

    df["close"] = df["close"].astype(float)

    # EMA 200
    df["ema200"] = df["close"].ewm(span=200).mean()

    latest_price = df["close"].iloc[-1]
    ema = df["ema200"].iloc[-1]

    trend = "bullish" if latest_price > ema else "bearish"

    return Response({
        "symbol": symbol,
        "price": latest_price,
        "ema200": ema,
        "trend": trend
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