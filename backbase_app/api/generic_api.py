import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backbase_project.settings')

import django
django.setup()

from backbase_app.api.providers_api import ProvidersAPI
from backbase_app.api.internal_api import InternalAPI
from backbase_app.models import ProviderExchange
from typing import Dict, List, Optional, Any, Union

import aiohttp
import asyncio
from django.conf import settings
from asgiref.sync import sync_to_async

@sync_to_async
def get_provider_exchange(providers: Optional[List[str]] = None) -> Optional[ProviderExchange]:
    """
    Get the highest priority provider that is not in the excluded list.
    
    Args:
        providers: List of provider IDs to exclude from the search
        
    Returns:
        Optional[ProviderExchange]: The selected provider or None if no providers are available
    """
    if providers:
        exchange = ProviderExchange.objects.filter(activated=True).exclude(id_name__in=providers).order_by('-priority').first()
    else:
        exchange = ProviderExchange.objects.filter(activated=True).order_by('-priority').first()
    return exchange

@sync_to_async
def get_all_providers() -> List[str]:
    """
    Get all active provider IDs ordered by priority.
    
    Returns:
        List[str]: List of provider IDs or empty list if an error occurs
    """
    try:
        providers = ProviderExchange.objects.filter(activated=True).order_by('-priority').values_list('id_name', flat=True)
        return list(providers)
    except Exception as e:
        print(e)
        return []

class GenericAPI:
    """
    A generic API class that coordinates between internal and external providers.
    
    This class provides methods to fetch currency exchange rates and convert amounts,
    trying internal sources first and falling back to external providers if needed.
    
    Attributes:
        base_url (str): The base URL for internal API endpoints
        internal_api (InternalAPI): Instance of the internal API client
        providers_api (ProvidersAPI): Instance of the providers API client
    """
    
    def __init__(self) -> None:
        """
        Initialize the GenericAPI with internal and provider API clients.
        """
        self.base_url: str = settings.API_URL_INTERNAL + settings.API_VERSION_INTERNAL
        self.internal_api: InternalAPI = InternalAPI()
        self.providers_api: ProvidersAPI = ProvidersAPI()

    async def fetch(self, session: aiohttp.ClientSession, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make an HTTP GET request to the internal API endpoint.
        
        Args:
            session: The aiohttp client session
            endpoint: The API endpoint to call
            params: Query parameters for the request
            
        Returns:
            Dict[str, Any]: The JSON response from the API
        """
        url = f"{self.base_url}{endpoint}"
        async with session.get(url, params=params) as response:
            return await response.json()

    async def get_exchange_rate_data(self, source_currency: str, exchanged_currency: str, valuation_date: str) -> Dict[str, Any]:
        """
        Get exchange rate data, trying internal sources first and falling back to providers.
        
        Args:
            source_currency: The source currency code
            exchanged_currency: The target currency code
            valuation_date: The date for the exchange rate
            
        Returns:
            Dict[str, Any]: The exchange rate data
        """
        data = await self.internal_api.get_exchange_rate_data(source_currency, exchanged_currency, valuation_date)
        if data["rate_value"] is not None:
            return data

        providers_exclude: List[str] = []
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

    async def get_currency_rates_list(self, start_date: str, end_date: str, base: str, symbols: str) -> Dict[str, Dict[str, float]]:
        """
        Get currency rates for a date range, trying internal sources first and falling back to providers.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            base: The base currency code
            symbols: Comma-separated string of currency codes
            
        Returns:
            Dict[str, Dict[str, float]]: Dictionary of exchange rates for each date
        """
        data = await self.internal_api.get_currency_rates_list(start_date, end_date, base, symbols)

        symbols_list = symbols.split(", ")
        error = False
        if data:
            # check if exists data for all dates
            for date in data:
                if not data[date] or set(symbols_list) != set(list(data[date].keys())):
                    error = True
                    break

        if error:
            providers_exclude: List[str] = []
            providers = await get_all_providers()
            providers_totals = len(providers)
            count_providers = 0

            while error and count_providers < providers_totals:
                print(f"trying to get data excluding providers: {providers_exclude}")
                provider = await get_provider_exchange(providers=providers_exclude)
                provider_name = str(provider.id_name)
                data = await self.providers_api.get_time_series(start_date, end_date, base, symbols_list, provider_name)
                providers_exclude.append(provider.id_name)
                count_providers += 1
                error = False
                for date in data:
                    if not data[date] or set(symbols_list) != set(list(data[date].keys())):
                        error = True
                        break
        if error:
            return {}

        return data

    async def get_convert_amount(self, currency_base: str, currency_to_convert: str, amount: Union[int, float]) -> Dict[str, Any]:
        """
        Convert an amount between currencies, trying internal sources first and falling back to providers.
        
        Args:
            currency_base: The source currency code
            currency_to_convert: The target currency code
            amount: The amount to convert
            
        Returns:
            Dict[str, Any]: The conversion result
        """
        data = await self.internal_api.get_convert_amount(currency_base, currency_to_convert, amount)

        if data["value"] is not None:
            return data
        
        providers_exclude: List[str] = []
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
