# Django
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
import traceback

from rest_framework.authentication import SessionAuthentication

from .models import HistoryItem

# DRF
from rest_framework.decorators import api_view, permission_classes, authentication_classes
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


from rest_framework.decorators import api_view, permission_classes
from rest_framework import status

from .models import HistoryItem
from .serializers import HistoryItemSerializer


def history_page(request):
    return render(request, 'accounts/history.html')



from .utils import add_history_item



from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import PriceHistory
from .serializers import PriceHistorySerializer


from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response



@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def save_price_history(request):
    symbol = request.GET.get('symbol', 'BTCUSDT').upper()

    df = fetch_klines_df(symbol, interval='1M', limit=12)

    saved_items = []

    for _, row in df.iterrows():
        month = row["open_time"].date().replace(day=1)

        item, created = PriceHistory.objects.update_or_create(
            symbol=symbol,
            month=month,
            defaults={
                "open_price": float(row["open"]),
                "high_price": float(row["high"]),
                "low_price": float(row["low"]),
                "close_price": float(row["close"]),
            }
        )

        saved_items.append(item)

    serializer = PriceHistorySerializer(saved_items, many=True)

    return Response({
        "message": f"Price history saved for {symbol}",
        "symbol": symbol,
        "count": len(saved_items),
        "data": serializer.data
    })



@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def price_history_list(request):
    symbol = request.GET.get('symbol', 'BTCUSDT').upper()

    items = PriceHistory.objects.filter(symbol=symbol).order_by('-month')
    serializer = PriceHistorySerializer(items, many=True)

    return Response(serializer.data)





@api_view(['POST'])
@permission_classes([IsAuthenticated])
def some_action(request):
    # Your logic here

    add_history_item(
        user=request.user,
        action='Checked trend',
        details='User checked market trend.'
    )

    return Response({'message': 'Action completed.'})

@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def history_list(request):
    history_items = HistoryItem.objects.filter(user=request.user).order_by('-created_at')
    serializer = HistoryItemSerializer(history_items, many=True)
    return Response(serializer.data)


@api_view(['DELETE'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def history_clear(request):
    HistoryItem.objects.filter(user=request.user).delete()
    return Response(
        {'message': 'History cleared successfully.'},
        status=status.HTTP_200_OK
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
    symbol = request.GET.get('symbol', 'BTCUSDT').upper()

    df = fetch_klines_df(symbol)

    status, distance = compute_distance(df)

    if status == "too_close":
        logic = "Price is too close to resistance"
    elif status == "far":
        logic = "Price has enough space to resistance"
    elif status == "medium":
        logic = "Price is at a moderate distance from resistance"
    else:
        logic = "Distance status is unclear"

    return Response({
        "symbol": symbol,
        "distance": float(distance),
        "status": status,
        "logic": logic
    })



@api_view(['GET'])
def breakout_signal(request):
    symbol = request.GET.get('symbol', 'BTCUSDT').upper()

    df = fetch_klines_df(symbol)

    status, resistance = compute_breakout(df)

    if status == "confirmed":
        logic = "Price broke above resistance"
    elif status == "not_confirmed":
        logic = "Price has not confirmed breakout"
    else:
        logic = "Breakout status is unclear"

    return Response({
        "symbol": symbol,
        "status": status,
        "resistance": float(resistance),
        "logic": logic
    })




@api_view(['GET'])
def support_signal(request):
    symbol = request.GET.get('symbol', 'BTCUSDT').upper()

    df = fetch_klines_df(symbol)

    status, support = compute_support(df)

    status = str(status).lower().replace(" ", "_")

    if status == "bounce":
        logic = "Price is reacting positively from support"
    elif status == "breakdown":
        logic = "Price broke below support"
    elif status == "near_support":
        logic = "Price is close to support"
    elif status == "far":
        logic = "Price is far from support"
    else:
        logic = "Support reaction is unclear"

    return Response({
        "symbol": symbol,
        "status": status,
        "support": float(support),
        "logic": logic
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
        'message': 'JWT działa'
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





def extract_value(data, key=None, default="UNKNOWN"):
    # Extract value safely from dict, tuple, list or raw value
    if isinstance(data, dict):
        if key:
            return data.get(key, default)
        return default

    if isinstance(data, (tuple, list)):
        return data[0] if len(data) > 0 else default

    if data is None:
        return default

    return data


@api_view(["GET"])
def long_score(request):
    symbol = request.GET.get("symbol", "BTCUSDT").upper()

    try:
        df = fetch_klines_df(symbol, limit=200)

        trend_data = compute_trend(df)
        rsi_data = compute_rsi(df)
        volume_data = compute_volume(df)
        structure_data = compute_structure(df)
        breakout_data = compute_breakout(df)
        distance_data = compute_distance(df)
        support_data = compute_support(df)

        signals = {
            "trend": str(extract_value(trend_data, "trend")),
            "rsi": str(extract_value(rsi_data, "status")),
            "volume": str(extract_value(volume_data, "status")),
            "structure": str(extract_value(structure_data, "structure")),
            "breakout": str(extract_value(breakout_data, "status")),
            "distance": str(extract_value(distance_data, "status")),
            "support": str(extract_value(support_data, "status")),
        }

        score, reasons = calculate_score(signals)

        score = int(score)
        reasons = [str(reason) for reason in reasons]

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
        print("ERROR IN /api/score/:", e)

        if request.user.is_authenticated:
            add_history_item(
                user=request.user,
                action="Checked score",
                details=f"{symbol}: score={score}, probability={probability}"
            )

        return Response(
            {"error": str(e)},
            status=500
        )




# FRONTEND PAGES

def home(request):
    return render(request, 'accounts/home.html')


def frontend_login(request):
    return render(request, 'accounts/login.html')


def frontend_register(request):
    return render(request, 'accounts/register.html')


def profile_page(request):
    if request.user.is_authenticated:
        HistoryItem.objects.create(
            user=request.user,
            action="Viewed market signals",
            details="User opened market signals page"
        )

    return render(request, "accounts/profile.html")
