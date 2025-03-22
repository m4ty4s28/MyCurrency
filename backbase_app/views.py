from django.shortcuts import render
from rest_framework import viewsets
from backbase_app.models import CurrencyExchangeRate, Currency
from backbase_app.serializers import CurrencyExchangeSerializer, CurrencySerializer
from django.http import JsonResponse
from rest_framework.response import Response
from django.utils.dateparse import parse_date

class CurrencyViewSet(viewsets.ModelViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    lookup_field = 'symbol'

class CurrencyExchangeViewSet(viewsets.ModelViewSet):
    queryset = CurrencyExchangeRate.objects.all()
    serializer_class = CurrencyExchangeSerializer

class CurrencyExchangeAPIViewSet(viewsets.ModelViewSet):
    queryset = CurrencyExchangeRate.objects.all()
    serializer_class = CurrencyExchangeSerializer

    def get_queryset(self):
        queryset = CurrencyExchangeRate.objects.all()
        source_currency = self.request.query_params.get('source_currency', None)
        exchanged_currency = self.request.query_params.get('exchanged_currency', None)
        valuation_date = self.request.query_params.get('valuation_date', None)
        if source_currency is None and exchanged_currency is None and valuation_date is None:
            return queryset
        parsed_date = parse_date(valuation_date)
        if parsed_date is None:
            raise ValueError("Invalid date format. It must be in YYYY-MM-DD format.")
        if source_currency is not None and exchanged_currency is not None and valuation_date is not None:
            queryset = queryset.filter(source_currency__symbol=source_currency,
                                       exchanged_currency__symbol=exchanged_currency,
                                       valuation_date=valuation_date).order_by('-valuation_date')
        return queryset

    def list(self, request):
        try:
            queryset = self.get_queryset()
            if queryset.exists():
                rate_value = queryset.values_list('rate_value', flat=True).first()
                return Response({'rate_value': rate_value})
            return Response({'rate_value': None})
        except ValueError as e:
            return Response({'error': str(e)}, status=400)

def get_exchange_rate_data(request):
    #get_exchange_rate_data(source_currency, exchanged_currency, valuation_date, provider)
    # get data from backend,

    # if not, get data from providers (priority) and save it in the backend

    # if not data, continue with the next provider

    return JsonResponse({"data": "data"})
