
from django.db import models
from django.contrib.auth.models import User



class HistoryItem(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='history_items'
    )
    action = models.CharField(max_length=255)
    details = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} - {self.action}'


class PriceHistory(models.Model):
    symbol = models.CharField(max_length=20)
    month = models.DateField()

    open_price = models.FloatField()
    high_price = models.FloatField()
    low_price = models.FloatField()
    close_price = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-month']
        unique_together = ('symbol', 'month')

    def __str__(self):
        return f'{self.symbol} - {self.month} - Close: {self.close_price}'