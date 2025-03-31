from django.db import models
from django.utils import timezone
from django.utils.timezone import now
from typing import Any
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

class Currency(models.Model):
    """
    Model representing a currency in the system.
    
    Attributes:
        code (str): Unique ID
        name (str): Full name of the currency
        symbol (str): Currency symbol
    """
    code: str = models.CharField(max_length=3, unique=True)
    name: str = models.CharField(max_length=20, db_index=True)
    symbol: str = models.CharField(max_length=10)

    def __str__(self) -> str:
        """
        Returns the string representation of the currency.
        
        Returns:
            str: The currency symbol
        """
        return self.symbol

class CurrencyExchangeRate(models.Model):
    """
    Model representing an exchange rate between two currencies.
    
    Attributes:
        source_currency (Currency): The base currency for the exchange rate
        exchanged_currency (Currency): The target currency for the exchange rate
        valuation_date (date): The date for which the exchange rate is valid
        rate_value (Decimal): The actual exchange rate value
    """
    source_currency: Currency = models.ForeignKey(Currency, related_name='currency_src', on_delete=models.CASCADE)
    exchanged_currency: Currency = models.ForeignKey(Currency, related_name='currency_exc', on_delete=models.CASCADE)
    valuation_date: Any = models.DateField(db_index=True, default=now, blank=True)
    rate_value: Any = models.DecimalField(decimal_places=6, max_digits=18)

    class Meta:
        unique_together = ['source_currency', 'exchanged_currency', 'valuation_date']

    def __str__(self) -> str:
        """
        Returns the string representation of the exchange rate.
        
        Returns:
            str: A formatted string showing the currency pair
        """
        return f"{self.source_currency} - {self.exchanged_currency}"

class ProviderExchange(models.Model):
    """
    Model representing an exchange rate provider.
    
    Attributes:
        id_name (str): Unique identifier for the provider
        name (str): Display name of the provider
        priority (int): Priority order for the provider (higher number = higher priority)
        activated (bool): Whether the provider is currently active
    """
    id_name: str = models.CharField(max_length=10, unique=True, db_index=True)
    name: str = models.CharField(max_length=100)
    priority: int = models.PositiveIntegerField(default=0)
    activated: bool = models.BooleanField(default=True)

    def __str__(self) -> str:
        """
        Returns the string representation of the provider.
        
        Returns:
            str: A formatted string showing the provider name and priority
        """
        return f"{self.name} - {self.priority}"

@receiver(pre_save, sender=CurrencyExchangeRate)
def update_rate_if_exists(sender, instance, **kwargs):
    """
    """

    existing = CurrencyExchangeRate.objects.filter(
        source_currency=instance.source_currency,
        exchanged_currency=instance.exchanged_currency,
        valuation_date=instance.valuation_date
    ).first()

    if existing:
        if existing.rate_value != instance.rate_value:
            try:
                CurrencyExchangeRate.objects.filter(id=existing.id).update(rate_value=instance.rate_value)
            except Exception as e:
                pass