import aiohttp
import asyncio

SYMBOLS = ["EUR", "CHF", "USD", "GBP"]
API_URL_INTERNAL = "http://127.0.0.1:8000/"
API_VERSION_INTERNAL = "api/"
from django.utils import timezone

class InternalAPI:
    def __init__(self):
        self.base_url = API_URL_INTERNAL + API_VERSION_INTERNAL

    async def fetch(self, session, endpoint, params):
        url = f"{self.base_url}{endpoint}"
        async with session.get(url, params=params) as response:
            return await response.json()

    async def get_exchange_rate_data(self, source_currency, exchanged_currency, valuation_date):
        params = {'source_currency': source_currency, 'exchanged_currency': exchanged_currency, 'valuation_date': valuation_date}
        async with aiohttp.ClientSession() as session:
            return await self.fetch(session, 'currency_exchange_api', params)

    async def get_currency_rates_list(self, start_date, end_date, base, symbols):
        params = {'start_date': start_date, 'end_date': end_date, 'base': base, 'symbols': symbols}

        async with aiohttp.ClientSession() as session:
            data = await self.fetch(session, 'currency_rates_list_api', params)

        current_date = start_date
        current_date = timezone.datetime.strptime(current_date, '%Y-%m-%d')
        end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d')
        date_list = []
        data_return = {}
        
        while current_date <= end_date:
            date_list.append(current_date.strftime('%Y-%m-%d'))
            current_date += timezone.timedelta(days=1)
        
        for date in date_list:
            data_return[date] = {}
            for rate in data:
                if rate["valuation_date"] == date:
                    data_return[date][rate["exchanged_currency__symbol"]] = rate["rate_value"]

        return data_return

async def main():

    internal_api = InternalAPI()
    
    source_currency = "USD"
    exchanged_currency = "EUR"
    valuation_date = "2025-03-19"
    data = await internal_api.get_exchange_rate_data(source_currency, exchanged_currency, valuation_date)
    print(data)
    print("----------------")

    start_date = "2025-03-20"
    end_date = "2025-03-22"
    base = "USD"
    symbols = "EUR, GBP" #["EUR", "CHF", "USD", "GBP"]
    symbols = "GBP, EUR"
    data = await internal_api.get_currency_rates_list(start_date, end_date, base, symbols)
    print(data)
    

if __name__ == "__main__":
    asyncio.run(main())