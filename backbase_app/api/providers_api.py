import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backbase_project.settings')

import django
django.setup()

from backbase_app.models import CurrencyExchangeRate, Currency
from backbase_app.external_services.api_currencybeacon import CurrencyBeaconAPI
from backbase_app.external_services.api_mock import MockAPI
import asyncio


def run_asyncio_task(async_func, *args, **kwargs):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(async_func(*args, **kwargs))

from asgiref.sync import sync_to_async
from django.utils import timezone

@sync_to_async
def save_data_rate(base, symbol, rate_value, date=None):
    source_currency_obj = Currency.objects.get(symbol=base)
    exchanged_currency_obj = Currency.objects.get(symbol=symbol)
    try:
        if not date:
            date = timezone.now().date()
        currency_exchange_exists = CurrencyExchangeRate.objects.filter(
            source_currency=source_currency_obj,
            exchanged_currency=exchanged_currency_obj,
            valuation_date=date,
        ).first()

        if currency_exchange_exists:
            print("update rate value in database")
            currency_exchange_exists.rate_value = float(rate_value)
            currency_exchange_exists.save()
        else:
            print("create rate value in database")
            CurrencyExchangeRate.objects.create(
                source_currency=source_currency_obj,
                exchanged_currency=exchanged_currency_obj,
                valuation_date=date,
                rate_value=rate_value
            )

        return {"rate_value" : rate_value}
    except Exception as e:
        print(e)

    return {"rate_value" : None}


@sync_to_async
def save_data_time_series(data, base):
    base_currency_obj = Currency.objects.get(symbol=base)
    for date, symbols in data.items():
            date_obj = timezone.datetime.strptime(date, '%Y-%m-%d')
            for symbol, rate_value in symbols.items():
                symbol_obj = Currency.objects.get(symbol=symbol)
                if not CurrencyExchangeRate.objects.filter(
                    source_currency=base_currency_obj,
                    exchanged_currency=symbol_obj,
                    valuation_date=date_obj,
                ).exists():
                    CurrencyExchangeRate.objects.create(
                        source_currency=base_currency_obj,
                        exchanged_currency=symbol_obj,
                        valuation_date=date_obj,
                        rate_value=float(rate_value)
                                    )

@sync_to_async
def save_data_convert(from_currency, to_currency, rate_value):
    source_currency_obj = Currency.objects.get(symbol=from_currency)
    exchanged_currency_obj = Currency.objects.get(symbol=to_currency)

    try:
        CurrencyExchangeRate.objects.create(
                source_currency=source_currency_obj,
                exchanged_currency=exchanged_currency_obj,
                rate_value=rate_value
            )
    except Exception as e:
        print(e)


class ProvidersAPI():

    def __init__(self):
        self.mock_api = MockAPI()
        self.cb_api = CurrencyBeaconAPI()
        self.provider_map = {
            "MC": self.mock_api,
            "CB": self.cb_api
        }

    async def get_latest_rates(self, base, symbols, provider):
        data =  await self.provider_map[provider].get_latest_rates(base, symbols)
        data_rate_value = {}
        if data:
            print(f"save data in database with provider {provider}")
            for symbol in symbols:
                rate_value = float(data["rates"][symbol])
                rate_value_symbol = await save_data_rate(base, symbol, rate_value)
                if not rate_value_symbol:
                    print(f"Error to save in database with provider {provider}")
                    data_rate_value[symbol] = None
                    continue
                data_rate_value[symbol] = rate_value_symbol["rate_value"]

        return data_rate_value


    async def get_historical_rates(self, date, base, symbols, provider):
        data =  await self.provider_map[provider].get_historical_rates(date, base, symbols)
        data_rate_value = {}
        if data:
            print(f"save data in database with provider {provider}")
            for symbol in symbols:
                rate_value = float(data["rates"][symbol])
                rate_value_symbol = await save_data_rate(base, symbol, rate_value, date)
                if not rate_value_symbol:
                    print(f"Error to save in database with provider {provider}")
                    data_rate_value[symbol] = None
                    continue
                data_rate_value[symbol] = rate_value_symbol["rate_value"]

        return data_rate_value

    async def convert_currency(self, from_currency, to_currency, amount, provider):
        data = await self.provider_map[provider].convert_currency(from_currency, to_currency, amount)

        rate_value = float(data["value"]/amount)

        await save_data_convert(from_currency, to_currency, rate_value)

        return data


    async def get_time_series(self, start_date, end_date, base, symbols, provider):
        data = await self.provider_map[provider].get_time_series(start_date, end_date, base, symbols)
        await save_data_time_series(data, base)
        return data


async def main():

    api = ProvidersAPI()


    symbols = ["EUR", "CHF", "USD", "GBP"]
    symbols = ["EUR"] #, "CHF", "USD", "GBP"]

    base = "USD"

    """
    data = await api.get_latest_rates(base, symbols, "MC")
    print(data)
    print("----------------")
    data = await api.get_latest_rates( base, symbols, "CB")
    print(data)
    #sys.exit()

    date = "2025-03-19"
    base = "USD"
    symbols = ["EUR", "CHF", "USD", "GBP"]
    symbols = ["EUR"] #, "CHF", "USD", "GBP"]
    data = await api.get_historical_rates(date, base, symbols, "MC")
    print(data)

    data = await api.get_historical_rates(date, base, symbols, "CB")
    print(data)
    
    #sys.exit()

    """
    print("----------------")
    data = await api.convert_currency("USD", "EUR", 100, "MC")
    print(data)
    print("----------------")
    currency_to_convert = "EUR"
    currency_base = "CHF"
    amount = 100
    data = await api.convert_currency(currency_to_convert, currency_base, amount, "CB")
    print(data)
    print("---------------")
    start_date = "2025-03-20"
    end_date = "2025-03-22"
    data = await api.get_time_series(start_date, end_date, 'USD', ["EUR", "CHF", "USD", "GBP"], "MC")
    print(data)
    print("----------------")
    data = await api.get_time_series(start_date, end_date, 'USD', ["EUR", "CHF", "USD", "GBP"], "CB")
    print(data)

if __name__ == "__main__":
    asyncio.run(main())