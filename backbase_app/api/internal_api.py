import aiohttp
import asyncio
from typing import Dict, List, Any, Optional, Union

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backbase_project.settings')

import django
django.setup()

from django.conf import settings
from django.utils import timezone

class InternalAPI:
    """
    A class that handles internal API requests for currency exchange operations.
    
    This class provides methods to interact with the internal API endpoints
    for retrieving exchange rates and performing currency conversions.
    
    Attributes:
        base_url (str): The base URL for the internal API
    """
    
    def __init__(self) -> None:
        """
        Initialize the InternalAPI with the base URL.
        """
        self.base_url: str = settings.API_URL_INTERNAL + settings.API_VERSION_INTERNAL

    async def fetch(self, session: aiohttp.ClientSession, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make an HTTP GET request to the specified endpoint.
        
        Args:
            session: The aiohttp client session to use for the request
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
        Get exchange rate data for a specific currency pair and date.
        
        Args:
            source_currency: The source currency code
            exchanged_currency: The target currency code
            valuation_date: The date in YYYY-MM-DD format
            
        Returns:
            Dict[str, Any]: The exchange rate data from the API
        """
        params = {'source_currency': source_currency, 'exchanged_currency': exchanged_currency, 'valuation_date': valuation_date}
        async with aiohttp.ClientSession() as session:
            return await self.fetch(session, 'currency_exchange_api', params)

    async def get_currency_rates_list(self, start_date: str, end_date: str, base: str, symbols: str) -> Dict[str, Dict[str, float]]:
        """
        Get a list of currency rates for a date range.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            base: The base currency code
            symbols: Comma-separated string of target currency codes
            
        Returns:
            Dict[str, Dict[str, float]]: Dictionary of exchange rates for each date and currency
        """
        params = {'start_date': start_date, 'end_date': end_date, 'base': base, 'symbols': symbols}

        async with aiohttp.ClientSession() as session:
            data = await self.fetch(session, 'currency_rates_list_api', params)

        current_date = start_date
        current_date = timezone.datetime.strptime(current_date, '%Y-%m-%d')
        end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d')
        date_list: List[str] = []
        data_return: Dict[str, Dict[str, float]] = {}
        
        while current_date <= end_date:
            date_list.append(current_date.strftime('%Y-%m-%d'))
            current_date += timezone.timedelta(days=1)
        for date in date_list:
            data_return[date] = {}
            for rate in data:
                if rate["valuation_date"] == date:
                    data_return[date][rate["exchanged_currency__symbol"]] = rate["rate_value"]

        return data_return

    async def get_convert_amount(self, currency_base: str, currency_to_convert: str, amount: Union[int, float]) -> Dict[str, Any]:
        """
        Convert an amount between currencies using current exchange rates.
        
        Args:
            currency_base: The source currency code
            currency_to_convert: The target currency code
            amount: The amount to convert
            
        Returns:
            Dict[str, Any]: Dictionary containing conversion details including timestamp, date, currencies, and converted value
        """
        source_currency = currency_base
        exchanged_currency = currency_to_convert
        valuation_date = str(timezone.now().date())

        params = {'source_currency': source_currency, 'exchanged_currency': exchanged_currency, 'valuation_date': valuation_date}

        async with aiohttp.ClientSession() as session:
            data = await self.fetch(session, 'currency_exchange_api', params)

        rate_value: Optional[float] = None
        if data["rate_value"] is not None:
            rate_value = float(data["rate_value"]) * float(amount)

        date_obj = timezone.datetime.strptime(valuation_date, '%Y-%m-%d')
        data_return = {
            "timestamp": int(timezone.datetime.timestamp(date_obj)),
            "date": valuation_date,
            "from": source_currency,
            "to": exchanged_currency,
            "amount": amount,
            "value": rate_value
        }

        return data_return
