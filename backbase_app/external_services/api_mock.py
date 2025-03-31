import aiohttp
import asyncio
import random
from django.utils import timezone
from datetime import datetime
from typing import Dict, List, Optional, Union, Any
from django.utils.timezone import datetime as timezone_datetime

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backbase_project.settings')

import django
django.setup()
from django.conf import settings

class MockAPI:
    """
    A mock API class that simulates currency exchange rate responses.
    
    This class provides mock implementations of currency exchange rate methods,
    generating random but realistic-looking exchange rate data.
    
    Attributes:
        api_key (str): The mock API key
        base_url (str): The mock API base URL
    """
    
    def __init__(self) -> None:
        """
        Initialize the MockAPI with mock API key and base URL.
        """
        self.api_key: str = settings.API_KEY_MOCK
        self.base_url: str = settings.API_URL_MOCK + settings.API_VERSION_MOCK

    async def get_latest_rates(self, base: str = 'USD', symbols: List[str] = []) -> Dict[str, Any]:
        """
        Get mock latest exchange rates for specified currencies.
        
        Args:
            base: The base currency code (default: 'USD')
            symbols: List of currency codes to get rates for
            
        Returns:
            Dict[str, Any]: A dictionary containing mock exchange rates
        """
        now = timezone.now()
        mock_data: Dict[str, Any] = {
            "date": now.strftime('%Y-%m-%d'),
            "base": base,
            "rates": {}
        }
        for symbol in symbols:
            if symbol == base:
                mock_data["rates"][symbol] = 1    
                continue
            mock_data["rates"][symbol] = round(random.uniform(0, 1), 8)

        return mock_data

    async def convert_currency(self, from_currency: str, to_currency: str, amount: Union[int, float]) -> Dict[str, Any]:
        """
        Convert an amount between currencies using mock rates.
        
        Args:
            from_currency: The source currency code
            to_currency: The target currency code
            amount: The amount to convert
            
        Returns:
            Dict[str, Any]: A dictionary containing the conversion result
        """
        date = timezone.now()
        mock_data: Dict[str, Any] = {
            "timestamp": int(timezone_datetime.timestamp(date)),
            "date": date.strftime('%Y-%m-%d'),
            "from": from_currency,
            "to": to_currency,
            "amount": amount,
            "value": round(random.uniform(30, 160), 8) if from_currency != to_currency else amount
        }
        return mock_data

    async def get_time_series(self, start_date: Union[str, timezone_datetime], 
                            end_date: Union[str, timezone_datetime], 
                            base: str = 'USD', 
                            symbols: Optional[List[str]] = None) -> Dict[str, Dict[str, float]]:
        """
        Get mock exchange rates for a date range.
        
        Args:
            start_date: Start date in YYYY-MM-DD format or datetime object
            end_date: End date in YYYY-MM-DD format or datetime object
            base: The base currency code (default: 'USD')
            symbols: List of currency codes to get rates for
            
        Returns:
            Dict[str, Dict[str, float]]: A dictionary containing exchange rates for each date
            
        Raises:
            ValueError: If start_date is greater than end_date
        """
        date_list: List[str] = []
        if start_date > end_date:
            raise ValueError("start_date must be less than or equal to end_date")
        
        if isinstance(start_date, str):
            start_date = timezone_datetime.strptime(start_date, '%Y-%m-%d')

        if isinstance(end_date, str):
            end_date = timezone_datetime.strptime(end_date, '%Y-%m-%d')
            
        current_date = start_date
        while current_date <= end_date:
            date_list.append(current_date.strftime('%Y-%m-%d'))
            current_date += timezone.timedelta(days=1)

        mock_data: Dict[str, Dict[str, float]] = {}
        for symbol in symbols:
            for date in date_list:
                if date not in mock_data:
                    mock_data[date] = {}
                if symbol == base:
                    mock_data[date][symbol] = 1
                    continue
                mock_data[date][symbol] = round(random.uniform(0, 1), 8)

        return mock_data

    async def get_historical_rates(self, date: str, base: str = 'USD', 
                                 symbols: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get mock historical exchange rates for a specific date.
        
        Args:
            date: The date in YYYY-MM-DD format
            base: The base currency code (default: 'USD')
            symbols: List of currency codes to get rates for
            
        Returns:
            Dict[str, Any]: A dictionary containing mock historical exchange rates
        """
        date = timezone_datetime.strptime(date, '%Y-%m-%d')
        mock_data: Dict[str, Any] = {
            "date": date.strftime('%Y-%m-%d'),
            "base": base,
            "rates": {}
        }
        for symbol in symbols:
            if symbol == base:
                mock_data["rates"][symbol] = 1    
                continue
            mock_data["rates"][symbol] = round(random.uniform(0, 1), 8)

        return mock_data

async def main() -> None:
    """
    Main function to demonstrate the usage of MockAPI.
    This function is used for testing purposes and should not be called in production.
    """
    mock_api = MockAPI()
    SYMBOLS = ["EUR", "CHF", "USD", "GBP"]

    date = "2025-03-18"
    base = "USD"
    latest_rates = await mock_api.get_historical_rates(date, base, symbols=SYMBOLS)
    print(latest_rates)

    print("----")

    latest_rates = await mock_api.get_latest_rates(symbols=SYMBOLS)
    print(latest_rates)

    print("----")

    currency_to_convert = "EUR"
    currency_base = "USD"
    amount = 100
    conversion_result = await mock_api.convert_currency(currency_base, currency_to_convert, amount)
    print(conversion_result)

    start_date = "2025-03-18"
    end_date = "2025-03-20"
    
    time_series = await mock_api.get_time_series(start_date, end_date, 'USD', SYMBOLS)
    print(time_series)

if __name__ == "__main__":
    asyncio.run(main())