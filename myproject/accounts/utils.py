from .models import HistoryItem


MAX_HISTORY_ITEMS = 30


def add_history_item(user, action, details=None):
    # Create lightweight history item
    HistoryItem.objects.create(
        user=user,
        action=action,
        details=details
    )

    # Keep only latest MAX_HISTORY_ITEMS records
    old_items = HistoryItem.objects.filter(user=user).order_by('-created_at')[MAX_HISTORY_ITEMS:]

    if old_items:
        old_ids = [item.id for item in old_items]
        HistoryItem.objects.filter(id__in=old_ids).delete()