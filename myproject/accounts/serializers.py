
from rest_framework import serializers
from .models import HistoryItem, PriceHistory



class HistoryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoryItem
        fields = "__all__"


class PriceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceHistory
        fields = [
            "id",
            "symbol",
            "month",
            "open_price",
            "high_price",
            "low_price",
            "close_price",
            "created_at",
        ]
