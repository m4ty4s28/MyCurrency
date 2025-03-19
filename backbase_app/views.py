from django.shortcuts import render
from rest_framework import viewsets
from backbase_app.models import CurrencyExchangeRate
from backbase_app.serializers import CurrencyExchangeSerializer

class CurrencyExchangeViewSet(viewsets.ModelViewSet):
    queryset = CurrencyExchangeRate.objects.all()
    serializer_class = CurrencyExchangeSerializer
