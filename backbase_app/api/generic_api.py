
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backbase_project.settings')

import django
django.setup()

from backbase_app.api.providers_api import ProvidersAPI
from backbase_app.api.internal_api import InternalAPI
from backbase_app.models import CurrencyExchangeRate, Currency, ProviderExchange

import aiohttp
import asyncio

SYMBOLS = ["EUR", "CHF", "USD", "GBP"]
API_URL_INTERNAL = "http://127.0.0.1:8000/"
API_VERSION_INTERNAL = "api/"


from asgiref.sync import sync_to_async

@sync_to_async
def get_provider_exchange(providers=None):
    if providers:
        exchange = ProviderExchange.objects.filter(activated=True).exclude(id_name__in=providers).order_by('-priority').first()
    else:
        exchange = ProviderExchange.objects.filter(activated=True).order_by('-priority').first()
    return exchange

class GenericAPI:
    def __init__(self):
        self.base_url = API_URL_INTERNAL + API_VERSION_INTERNAL
        self.internal_api = InternalAPI()
        self.providers_api = ProvidersAPI()

    async def fetch(self, session, endpoint, params):
        url = f"{self.base_url}{endpoint}"
        async with session.get(url, params=params) as response:
            return await response.json()

    async def get_exchange_rate_data(self, source_currency, exchanged_currency, valuation_date):
        data = await self.internal_api.get_exchange_rate_data(source_currency, exchanged_currency, valuation_date)
        print("1", data)
        if data["rate_value"] is None:
            provider = await get_provider_exchange()
            provider_name = str(provider.id_name)
            data = await self.providers_api.get_historical_rates(valuation_date, source_currency, [exchanged_currency], provider_name)
            print("2", data)

async def main():
    generic_api = GenericAPI()
    
    source_currency = "USD"
    exchanged_currency = "EUR"
    valuation_date = "2025-03-13"
    data = await generic_api.get_exchange_rate_data(source_currency, exchanged_currency, valuation_date)
    print("data", data)

if __name__ == "__main__":
    asyncio.run(main())

