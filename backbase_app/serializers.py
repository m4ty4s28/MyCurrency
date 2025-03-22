from rest_framework import serializers
from backbase_app.models import CurrencyExchangeRate, Currency, ProviderExchange

class CurrencySerializer(serializers.ModelSerializer):

    class Meta:
        model = Currency
        fields = '__all__'


class CurrencyExchangeSerializer(serializers.ModelSerializer):

    source_currency = serializers.StringRelatedField()
    exchanged_currency = serializers.StringRelatedField()

    class Meta:
        model = CurrencyExchangeRate
        #fields = ('source_currency', 'exchanged_currency', 'rate_value')
        fields = '__all__'
