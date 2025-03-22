import aiohttp
import asyncio
import random
from django.utils import timezone
from datetime import datetime


import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backbase_project.settings')

import django
django.setup()

API_KEY_MOCK = "123456789"
API_URL_MOCK = "https://api.example.com/"
API_VERSION_MOCK = "v1/"

class MockAPI:
    def __init__(self):
        self.api_key = API_KEY_MOCK
        self.base_url = API_URL_MOCK + API_VERSION_MOCK

    async def get_latest_rates(self, base: str = 'USD', symbols: list = []):
        now = timezone.now()
        mock_data = {
            "date" : now.strftime('%Y-%m-%d'),
            "base" : base,
            "rates" : {}
        }
        for symbol in symbols:
            if symbol == base:
                mock_data["rates"][symbol] = 1    
                continue
            mock_data["rates"][symbol] = round(random.uniform(0, 1), 8)

        return mock_data

    async def convert_currency(self, from_currency, to_currency, amount):
        date = timezone.now()
        mock_data = {
            "timestamp" : int(timezone.datetime.timestamp(date)),
            "date" : date.strftime('%Y-%m-%d'),
            "from" : from_currency,
            "to" : to_currency,
            "amount" : amount,
            "value" : round(random.uniform(30, 160), 8) if from_currency != to_currency else amount
        }
        return mock_data

    async def get_time_series(self, start_date, end_date, base='USD', symbols=None):
        
        date_list = []
        if start_date > end_date:
            raise ValueError("start_date must be less than or equal to end_date")
        
        if isinstance(start_date, str):
            start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d')

        if isinstance(end_date, str):
            end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d')
            
        current_date = start_date
        while current_date <= end_date:
            date_list.append(current_date.strftime('%Y-%m-%d'))
            current_date += timezone.timedelta(days=1)

        mock_data = {}
        for symbol in symbols:
            for date in date_list:
                if date not in mock_data:
                    mock_data[date] = {}
                if symbol == base:
                    mock_data[date][symbol] =   1
                    continue
                mock_data[date][symbol] = round(random.uniform(0, 1), 8)

        return mock_data

    async def get_historical_rates(self, date, base='USD', symbols=None):
        date = timezone.datetime.strptime(date, '%Y-%m-%d')
        mock_data = {
            "date" : date.strftime('%Y-%m-%d'),
            "base" : base,
            "rates" : {}
        }
        for symbol in symbols:
            if symbol == base:
                mock_data["rates"][symbol] = 1    
                continue
            mock_data["rates"][symbol] = round(random.uniform(0, 1), 8)

        return mock_data

async def main():

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