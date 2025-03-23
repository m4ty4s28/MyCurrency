import aiohttp
import asyncio

SYMBOLS = ["EUR", "CHF", "USD", "GBP"]
API_KEY = "mE41rNwTjgGW9xfz1mBY9JSQCSP3BqKF"
API_URL_CURRENCYBE = "https://api.currencybeacon.com/"
API_VERSION_CURRENCYBE = "v1/"

class CurrencyBeaconAPI:
    def __init__(self):
        self.api_key = API_KEY
        self.base_url = API_URL_CURRENCYBE + API_VERSION_CURRENCYBE

    async def fetch(self, session, endpoint, params):
        url = f"{self.base_url}{endpoint}"
        params['api_key'] = self.api_key
        async with session.get(url, params=params) as response:
            return await response.json()

    async def get_latest_rates(self, base='USD', symbols=None):
        params = {'base': base}
        if symbols:
            params['symbols'] = ','.join(symbols)
        async with aiohttp.ClientSession() as session:
            data = await self.fetch(session, 'latest', params)
            return data["response"]

    async def convert_currency(self, from_currency, to_currency, amount):
        params = {'from': from_currency, 'to': to_currency, 'amount': amount}
        async with aiohttp.ClientSession() as session:
            data = await self.fetch(session, 'convert', params)
            return data["response"]

    async def get_historical_rates(self, date, base='USD', symbols=None):
        params = {'base': base, 'date': date}
        if symbols:
            params['symbols'] = ','.join(symbols)
        async with aiohttp.ClientSession() as session:
            data = await self.fetch(session, 'historical', params)
            return data["response"]

    async def get_time_series(self, start_date, end_date, base='USD', symbols=None):
        params = {'base': base, 'start_date': start_date, 'end_date': end_date}
        if symbols:
            params['symbols'] = ','.join(symbols)
        async with aiohttp.ClientSession() as session:
            data = await self.fetch(session, 'timeseries', params)
            return data["response"]
        

async def main():

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
    #YYYY-MM-DD
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