import aiohttp
import asyncio

SYMBOLS = ["EUR", "CHF", "USD", "GBP"]
API_URL_INTERNAL = "http://127.0.0.1:8000/"
API_VERSION_INTERNAL = "api/"

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

async def main():

    internal_api = InternalAPI()
    
    source_currency = "USD"
    exchanged_currency = "EUR"
    valuation_date = "2025-03-19"
    data = await internal_api.get_exchange_rate_data(source_currency, exchanged_currency, valuation_date)
    print(data)
    

if __name__ == "__main__":
    asyncio.run(main())