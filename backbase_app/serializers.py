from rest_framework import serializers
from typing import Any, Dict

from backbase_app.models import Currency, CurrencyExchangeRate

class CurrencySerializer(serializers.ModelSerializer):
    """
    Serializer for the Currency model.
    Handles serialization and deserialization of Currency objects.
    """
    class Meta:
        model = Currency
        fields: list[str] = ['id', 'code', 'name', 'symbol']


class CurrencyExchangeSerializer(serializers.ModelSerializer):
    """
    Serializer for the CurrencyExchangeRate model.
    Handles serialization and deserialization of CurrencyExchangeRate objects.
    """
    source_currency = serializers.StringRelatedField()
    exchanged_currency = serializers.StringRelatedField()

    class Meta:
        model = CurrencyExchangeRate
        fields: list[str] = ['id', 'source_currency', 'exchanged_currency', 'valuation_date', 'rate_value']
