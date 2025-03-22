from celery import shared_task
import asyncio
import logging
from backbase_app.external_services.api_currencybeacon import CurrencyBeaconAPI
from backbase_app.models import Currency, CurrencyExchangeRate, ProviderExchange

logger = logging.getLogger(__name__)

def run_asyncio_task(async_func, *args, **kwargs):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(async_func(*args, **kwargs))
