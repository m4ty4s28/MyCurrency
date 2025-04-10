import aiohttp
import asyncio
from typing import Dict, List, Optional, Any, Union
from django.conf import settings

class CurrencyBeaconAPI:
    """
    A class to interact with the CurrencyBeacon API.
    
    This class provides methods to fetch currency exchange rates, convert currencies,
    and retrieve historical exchange rate data.
    
    Attributes:
        api_key (str): The API key for authentication
        base_url (str): The base URL for the API endpoints
    """
    
    def __init__(self) -> None:
        """
        Initialize the CurrencyBeaconAPI with API key and base URL.
        """
        self.api_key: str = settings.API_KEY_CURRENCYBE
        self.base_url: str = settings.API_URL_CURRENCYBE + settings.API_VERSION_CURRENCYBE

    async def fetch(self, session: aiohttp.ClientSession, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make an HTTP GET request to the API endpoint.
        
        Args:
            session: The aiohttp client session
            endpoint: The API endpoint to call
            params: Query parameters for the request
            
        Returns:
            Dict[str, Any]: The JSON response from the API
        """
        try:
            url = f"{self.base_url}{endpoint}"
            params['api_key'] = self.api_key
            async with session.get(url, params=params) as response:
                return await response.json()
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            raise

    async def get_latest_rates(self, base: str = 'USD', symbols: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get the latest exchange rates for specified currencies.
        
        Args:
            base: The base currency code (default: 'USD')
            symbols: List of currency codes to get rates for
            
        Returns:
            Dict[str, Any]: The latest exchange rates
        """
        params: Dict[str, Any] = {'base': base}
        if symbols:
            params['symbols'] = ','.join(symbols)
        async with aiohttp.ClientSession() as session:
            data = await self.fetch(session, 'latest', params)
            return data["response"]

    async def convert_currency(self, from_currency: str, to_currency: str, amount: Union[int, float]) -> Dict[str, Any]:
        """
        Convert an amount from one currency to another.
        
        Args:
            from_currency: The source currency code
            to_currency: The target currency code
            amount: The amount to convert
            
        Returns:
            Dict[str, Any]: The conversion result
        """
        params: Dict[str, Any] = {'from': from_currency, 'to': to_currency, 'amount': amount}
        async with aiohttp.ClientSession() as session:
            data = await self.fetch(session, 'convert', params)
            return data["response"]

    async def get_historical_rates(self, date: str, base: str = 'USD', symbols: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get historical exchange rates for a specific date.
        
        Args:
            date: The date in YYYY-MM-DD format
            base: The base currency code (default: 'USD')
            symbols: List of currency codes to get rates for
            
        Returns:
            Dict[str, Any]: The historical exchange rates
        """
        params: Dict[str, Any] = {'base': base, 'date': date}
        if symbols:
            params['symbols'] = ','.join(symbols)
        async with aiohttp.ClientSession() as session:
            data = await self.fetch(session, 'historical', params)
            return data["response"]

    async def get_time_series(self, start_date: str, end_date: str, base: str = 'USD', symbols: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get exchange rates for a date range.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            base: The base currency code (default: 'USD')
            symbols: List of currency codes to get rates for
            
        Returns:
            Dict[str, Any]: The time series exchange rates
        """
        params: Dict[str, Any] = {'base': base, 'start_date': start_date, 'end_date': end_date}
        if symbols:
            params['symbols'] = ','.join(symbols)
        async with aiohttp.ClientSession() as session:
            data = await self.fetch(session, 'timeseries', params)
            return data["response"]
