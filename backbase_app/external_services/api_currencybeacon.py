import aiohttp
import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import date

SYMBOLS: List[str] = ["EUR", "CHF", "USD", "GBP"]
API_KEY: str = "mE41rNwTjgGW9xfz1mBY9JSQCSP3BqKF"
API_URL_CURRENCYBE: str = "https://api.currencybeacon.com/"
API_VERSION_CURRENCYBE: str = "v1/"

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
        self.api_key: str = API_KEY
        self.base_url: str = API_URL_CURRENCYBE + API_VERSION_CURRENCYBE

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
        url = f"{self.base_url}{endpoint}"
        params['api_key'] = self.api_key
        async with session.get(url, params=params) as response:
            return await response.json()

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

async def main() -> None:
    """
    Main function to demonstrate the usage of CurrencyBeaconAPI.
    This function is used for testing purposes and should not be called in production.
    """
    cb_api = CurrencyBeaconAPI()
    SYMBOLS = ["EUR", "CHF", "USD", "GBP"]
    
    latest_rates = await cb_api.get_latest_rates(symbols=SYMBOLS)
    print(latest_rates)
    
    currency_base = "USD"
    currency_to_convert = "EUR"
    amount = 100
    conversion_result = await cb_api.convert_currency(currency_base, currency_to_convert, amount)
    print(conversion_result)

    print("----")
    base = "USD"
    date = "2025-03-16"
    conversion_result = await cb_api.get_historical_rates(date, base, SYMBOLS)
    print(conversion_result)

    print("---------")
    SYMBOLS = ["EUR", "GBP"]
    time_series = await cb_api.get_time_series('2025-03-20', '2025-03-22', base, SYMBOLS)
    print(time_series)

if __name__ == "__main__":
    asyncio.run(main())