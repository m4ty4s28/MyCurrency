from celery import shared_task
import asyncio
import logging
from backbase_app.models import Currency, CurrencyExchangeRate, ProviderExchange
from django.utils import timezone
from django.db import IntegrityError
from typing import Optional, List
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)

def run_asyncio_task(async_func, *args, **kwargs):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(async_func(*args, **kwargs))

@shared_task
def save_data_today():
    from backbase_app.api.providers_api import ProvidersAPI
    from backbase_app.api.generic_api import get_all_providers, get_provider_exchange

    providers_api = ProvidersAPI()

    symbols = list(Currency.objects.all().values_list("symbol", flat=True))
    base = "USD"

    provider = run_asyncio_task(get_provider_exchange)
    data = run_asyncio_task(providers_api.get_latest_rates, base, symbols, provider.id_name)

    providers_exclude = []
    providers = run_asyncio_task(get_all_providers)
    providers_totals = len(providers)
    count_providers = 0

    while data is None and count_providers < providers_totals:
        print(f"trying to get data excluding providers: {providers_exclude}")
        provider = run_asyncio_task(get_provider_exchange,providers_exclude)
        provider_name = str(provider.id_name)
        data = run_asyncio_task(providers_api.get_latest_rates, base, symbols, provider_name)
        providers_exclude.append(provider.id_name)
        count_providers += 1

