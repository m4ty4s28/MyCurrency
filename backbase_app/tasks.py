from celery import shared_task
import asyncio

from backbase_app.external_services.api_currencybeacon import CurrencyBeaconAPI

def run_asyncio_task(async_func, *args, **kwargs):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(async_func(*args, **kwargs))


cb_api = CurrencyBeaconAPI()

@shared_task
def get_latest_rates_task():
    return run_asyncio_task(cb_api.get_latest_rates)


@shared_task
def convert_currency_task(from_currency, to_currency, amount):
    return run_asyncio_task(cb_api.convert_currency, from_currency, to_currency, amount)

@shared_task
def add(x, y):
    return x + y