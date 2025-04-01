import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backbase_project.settings')

import django
django.setup()

from backbase_app.models import CurrencyExchangeRate, Currency
from backbase_app.external_services.api_currencybeacon import CurrencyBeaconAPI
from backbase_app.external_services.api_mock import MockAPI
from typing import Dict, List, Optional, Any, Union, Callable
import asyncio
from datetime import date
from asgiref.sync import sync_to_async
from django.utils import timezone

def run_asyncio_task(async_func: Callable, *args: Any, **kwargs: Any) -> Any:
    """
    Run an async function in a new event loop.
    
    Args:
        async_func: The async function to run
        *args: Positional arguments for the async function
        **kwargs: Keyword arguments for the async function
        
    Returns:
        Any: The result of the async function
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(async_func(*args, **kwargs))



@sync_to_async
def save_data_rate(base: str, symbol: str, rate_value: float, date: Optional[date] = None) -> Dict[str, Optional[float]]:
    """
    Save or update a currency exchange rate in the database.
    
    Args:
        base: The base currency code
        symbol: The target currency code
        rate_value: The exchange rate value
        date: Optional date for the exchange rate (defaults to current date)
        
    Returns:
        Dict[str, Optional[float]]: Dictionary containing the saved rate value or None if error occurs
    """
    source_currency_obj = Currency.objects.get(symbol=base)
    exchanged_currency_obj = Currency.objects.get(symbol=symbol)

    try:
        if not date:
            date = timezone.now().date()

        """ # other method with similar results
        try:
            CurrencyExchangeRate.objects.create(
                    source_currency=source_currency_obj,
                    exchanged_currency=exchanged_currency_obj,
                    valuation_date=date,
                    rate_value=rate_value
                )
        except Exception as e:
            #print(e)
            pass
        """

        currency_exchange_exists = CurrencyExchangeRate.objects.filter(
            source_currency=source_currency_obj,
            exchanged_currency=exchanged_currency_obj,
            valuation_date=date,
        ).first()

        if currency_exchange_exists:
            currency_exchange_exists.rate_value = float(rate_value)
            currency_exchange_exists.save()
        else:
            CurrencyExchangeRate.objects.create(
                source_currency=source_currency_obj,
                exchanged_currency=exchanged_currency_obj,
                valuation_date=date,
                rate_value=rate_value
            )

        return {"rate_value": rate_value}
    except Exception as e:
        print(e)

    return {"rate_value": None}

@sync_to_async
def save_data_time_series(data: Dict[str, Dict[str, float]], base: str) -> None:
    """
    Save multiple currency exchange rates for a time series in the database.
    
    Args:
        data: Dictionary containing exchange rates for different dates and currencies
        base: The base currency code
    """

    data_list = []
    base_currency_obj = Currency.objects.get(symbol=base)
    for date_str, symbols in data.items():
        date_obj = timezone.datetime.strptime(date_str, '%Y-%m-%d')
        for symbol, rate_value in symbols.items():
            symbol_obj = Currency.objects.get(symbol=symbol)
            data_list.append(
                CurrencyExchangeRate(
                    source_currency=base_currency_obj,
                    exchanged_currency=symbol_obj,
                    valuation_date=date_obj,
                    rate_value=float(rate_value)
                )
            )
    CurrencyExchangeRate.objects.bulk_create(data_list, batch_size=100, ignore_conflicts=True)

@sync_to_async
def save_data_convert(from_currency: str, to_currency: str, rate_value: float) -> None:
    """
    Save a currency conversion rate in the database.
    
    Args:
        from_currency: The source currency code
        to_currency: The target currency code
        rate_value: The conversion rate value
    """
    source_currency_obj = Currency.objects.get(symbol=from_currency)
    exchanged_currency_obj = Currency.objects.get(symbol=to_currency)

    try:
        CurrencyExchangeRate.objects.create(
            source_currency=source_currency_obj,
            exchanged_currency=exchanged_currency_obj,
            rate_value=rate_value
        )
    except Exception as e:
        pass

class ProvidersAPI:
    """
    A class that manages interactions with different currency exchange rate providers.
    
    This class coordinates between different API providers (Mock and CurrencyBeacon)
    and handles saving the exchange rate data to the database.
    
    Attributes:
        mock_api (MockAPI): Instance of the mock API client
        cb_api (CurrencyBeaconAPI): Instance of the CurrencyBeacon API client
        provider_map (Dict[str, Any]): Mapping of provider IDs to their API instances
    """
    
    def __init__(self) -> None:
        """
        Initialize the ProvidersAPI with available API clients.
        """
        self.mock_api: MockAPI = MockAPI()
        self.cb_api: CurrencyBeaconAPI = CurrencyBeaconAPI()
        self.provider_map: Dict[str, Any] = {
            "MC": self.mock_api,
            "CB": self.cb_api
        }

    async def get_latest_rates(self, base: str, symbols: List[str], provider: str) -> Dict[str, Optional[float]]:
        """
        Get latest exchange rates from a specific provider and save them to the database.
        
        Args:
            base: The base currency code
            symbols: List of target currency codes
            provider: The provider ID to use
            
        Returns:
            Dict[str, Optional[float]]: Dictionary of exchange rates for each currency
        """
        data = await self.provider_map[provider].get_latest_rates(base, symbols)
        data_rate_value: Dict[str, Optional[float]] = {}
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

    async def get_historical_rates(self, date: str, base: str, symbols: List[str], provider: str) -> Dict[str, Optional[float]]:
        """
        Get historical exchange rates from a specific provider and save them to the database.
        
        Args:
            date: The date in YYYY-MM-DD format
            base: The base currency code
            symbols: List of target currency codes
            provider: The provider ID to use
            
        Returns:
            Dict[str, Optional[float]]: Dictionary of exchange rates for each currency
        """
        data = await self.provider_map[provider].get_historical_rates(date, base, symbols)
        data_rate_value: Dict[str, Optional[float]] = {}
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

    async def convert_currency(self, from_currency: str, to_currency: str, amount: Union[int, float], provider: str) -> Dict[str, Any]:
        """
        Convert an amount between currencies using a specific provider.
        
        Args:
            from_currency: The source currency code
            to_currency: The target currency code
            amount: The amount to convert
            provider: The provider ID to use
            
        Returns:
            Dict[str, Any]: The conversion result
        """
        data = await self.provider_map[provider].convert_currency(from_currency, to_currency, amount)

        rate_value = float(data["value"]/amount)

        await save_data_convert(from_currency, to_currency, rate_value)

        return data

    async def get_time_series(self, start_date: str, end_date: str, base: str, symbols: List[str], provider: str, save_data: bool = True) -> Dict[str, Dict[str, float]]:
        """
        Get exchange rates for a date range from a specific provider.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            base: The base currency code
            symbols: List of target currency codes
            provider: The provider ID to use
            
        Returns:
            Dict[str, Dict[str, float]]: Dictionary of exchange rates for each date and currency
        """
        data = await self.provider_map[provider].get_time_series(start_date, end_date, base, symbols)
        if save_data:
            await save_data_time_series(data, base)
        return data
