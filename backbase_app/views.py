from django.shortcuts import render
from django.http import JsonResponse
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import csrf_exempt

from rest_framework import viewsets
from rest_framework.response import Response

from backbase_app.models import CurrencyExchangeRate, Currency
from backbase_app.serializers import CurrencyExchangeSerializer, CurrencySerializer
from backbase_app.api.generic_api import GenericAPI

import asyncio

def run_asyncio_task(async_func, *args, **kwargs):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(async_func(*args, **kwargs))


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

class CurrencyRateListAPIViewSet(viewsets.ModelViewSet):
    queryset = CurrencyExchangeRate.objects.all()
    serializer_class = CurrencyExchangeSerializer

    def get_queryset(self):
        queryset = CurrencyExchangeRate.objects.all()
       
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        base = self.request.query_params.get('base', None)
        symbols = self.request.query_params.get('symbols', None)
        if start_date is None and end_date is None and base is None and symbols is None:
            return queryset
        parsed_date_start = parse_date(start_date)
        parsed_date_end = parse_date(end_date)
        if parsed_date_start is None or parsed_date_end is None:
            raise ValueError("Invalid date format. It must be in YYYY-MM-DD format.")
        if start_date is not None and end_date is not None and base is not None and symbols is not None:
            queryset = queryset.filter(
                source_currency__symbol=base,
                exchanged_currency__symbol__in=list(map(str.strip, symbols.split(','))),
                valuation_date__gte=start_date,
                valuation_date__lte=end_date
            ).order_by('-valuation_date')
        return queryset

    def list(self, request):
        try:
            queryset = self.get_queryset()
            data = queryset.values('source_currency__symbol', 'exchanged_currency__symbol', 'rate_value', 'valuation_date')
            return Response(data)
        except ValueError as e:
            return Response({'error': str(e)}, status=400)


@csrf_exempt
def get_exchange_rate_data(request):

    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    
    generic_api = GenericAPI()

    source_currency = request.GET.get('source_currency', None)
    exchanged_currency = request.GET.get('exchanged_currency', None)
    valuation_date = request.GET.get('valuation_date', None)
    parsed_date = parse_date(valuation_date)

    if parsed_date is None:
        return JsonResponse({'error': 'Invalid date format. It must be in YYYY-MM-DD format.'}, status=400)
    if not source_currency or not exchanged_currency or not valuation_date:
        return JsonResponse({'error': 'Invalid parameters'}, status=400)
    
    print("source_currency", source_currency)
    print("exchanged_currency", exchanged_currency)
    print("valuation_date", valuation_date)
    
    data = run_asyncio_task(generic_api.get_exchange_rate_data, source_currency, exchanged_currency, valuation_date)
    print("data", data)

    return JsonResponse(data)

@csrf_exempt
def get_currency_rates_list(request):

    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    
    generic_api = GenericAPI()

    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)
    base = request.GET.get('base', None)
    symbols = request.GET.get('symbols', None)

    parsed_date_start = parse_date(start_date)
    parsed_date_end = parse_date(end_date)

    if parsed_date_start is None or parsed_date_end is None:
        return JsonResponse({'error': 'Invalid date format. It must be in YYYY-MM-DD format.'}, status=400)
    if not start_date or not end_date or not base or not symbols:
        return JsonResponse({'error': 'Invalid parameters'}, status=400)
    
    print("start_date", start_date)
    print("end_date", end_date)
    print("base", base)
    print("symbols", symbols)

    data = run_asyncio_task(generic_api.get_currency_rates_list, start_date, end_date, base, symbols)
    print("data", data)

    return JsonResponse(data)