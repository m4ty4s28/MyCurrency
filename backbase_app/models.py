from django.db import models
from django.utils import timezone

class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=20, db_index=True)
    symbol = models.CharField(max_length=10)

    def __str__(self):
        return self.symbol

class CurrencyExchangeRate(models.Model):
    source_currency = models.ForeignKey(Currency, related_name='currency_src', on_delete=models.CASCADE)
    exchanged_currency = models.ForeignKey(Currency, related_name='currency_exc', on_delete=models.CASCADE)
    valuation_date = models.DateField(db_index=True, default=timezone.now().date(), blank=True)
    rate_value = models.DecimalField(db_index=True, decimal_places=6, max_digits=18)

    def __str__(self):
            return f"{self.source_currency} - {self.exchanged_currency}"
