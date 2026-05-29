from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import HistoryItem, PriceHistory


@admin.register(HistoryItem)
class HistoryItemAdmin(admin.ModelAdmin):
    list_display = ("user", "action", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "action", "details")



@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "symbol",
        "month",
        "open_price",
        "high_price",
        "low_price",
        "close_price",
        "created_at",
    )

    list_filter = ("symbol", "month")
    search_fields = ("symbol",)
    readonly_fields = ("created_at",)