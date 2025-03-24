
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

@sync_to_async
def get_all_providers():
    try:
        providers = ProviderExchange.objects.filter(activated=True).order_by('-priority').values_list('id_name', flat=True)
        return list(providers)
    except Exception as e:
        print(e)
        return []

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
        if data["rate_value"] is not None:
            return data

        providers_exclude = []
        providers = await get_all_providers()
        providers_totals = len(providers)
        count_providers = 0

        while data["rate_value"] is None and count_providers < providers_totals:
            print(f"trying to get data excluding providers: {providers_exclude}")
            provider = await get_provider_exchange(providers=providers_exclude)
            provider_name = str(provider.id_name)
            data = await self.providers_api.get_historical_rates(valuation_date, source_currency, [exchanged_currency], provider_name)
            providers_exclude.append(provider.id_name)
            count_providers += 1
            data["rate_value"] = data[exchanged_currency]
            del data[exchanged_currency]

        return data

    async def get_currency_rates_list(self, start_date, end_date, base, symbols):
        data = await self.internal_api.get_currency_rates_list(start_date, end_date, base, symbols)

        symbols = symbols.split(", ")
        error = False
        if data:
            # check if exists data for all dates
            for date in data:
                if not data[date] or set(symbols) != set(list(data[date].keys())):
                    error = True
                    break

        if error:
            providers_exclude = []
            providers = await get_all_providers()
            providers_totals = len(providers)
            count_providers = 0

            while error and count_providers < providers_totals:
                print(f"trying to get data excluding providers: {providers_exclude}")
                provider = await get_provider_exchange(providers=providers_exclude)
                provider_name = str(provider.id_name)
                data = await self.providers_api.get_time_series(start_date, end_date, base, symbols, provider_name)
                providers_exclude.append(provider.id_name)
                count_providers += 1
                error = False
                for date in data:
                    if not data[date] or set(symbols) != set(list(data[date].keys())):
                        error = True
                        break
        if error:
            return {}

        return data

    async def get_convert_amount(self, currency_base, currency_to_convert, amount):
        data = await self.internal_api.get_convert_amount(currency_base, currency_to_convert, amount)

        if data["value"] is not None:
            return data
        
        providers_exclude = []
        providers = await get_all_providers()
        providers_totals = len(providers)
        count_providers = 0

        while data["value"] is None and count_providers < providers_totals:
            print(f"trying to get data excluding providers: {providers_exclude}")
            provider = await get_provider_exchange(providers=providers_exclude)
            provider_name = str(provider.id_name)
            data = await self.providers_api.convert_currency(currency_base, currency_to_convert, amount, provider_name)
            providers_exclude.append(provider.id_name)
            count_providers += 1
            data["value"] = data["value"]

        return data


async def main():
    generic_api = GenericAPI()
    """
    source_currency = "USD"
    exchanged_currency = "EUR"
    valuation_date = "2025-02-02"
    data = await generic_api.get_exchange_rate_data(source_currency, exchanged_currency, valuation_date)
    print("data", data)

    start_date = "2025-03-20"
    end_date = "2025-03-22"
    base = "USD"
    symbols = "GBP, EUR"
    data = await generic_api.get_currency_rates_list(start_date, end_date, base, symbols)
    print(data)
    """
    currency_base = "USD"
    currency_to_convert = "EUR"
    amount = 100
    data = await generic_api.get_convert_amount(currency_base, currency_to_convert, amount)
    print(data)


if __name__ == "__main__":
    asyncio.run(main())

