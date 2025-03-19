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
            return await self.fetch(session, 'latest', params)

    async def convert_currency(self, from_currency, to_currency, amount):
        params = {'from': from_currency, 'to': to_currency, 'amount': amount}
        async with aiohttp.ClientSession() as session:
            return await self.fetch(session, 'convert', params)

async def main():

    cb_api = CurrencyBeaconAPI()
    
    latest_rates = await cb_api.get_latest_rates(symbols=SYMBOLS)
    #print(latest_rates)
    print(latest_rates["response"]["rates"])
    
    conversion_result = await cb_api.convert_currency('EUR', 'USD', 100)
    #print(conversion_result)
    print(conversion_result["response"]["value"])
    

if __name__ == "__main__":
    asyncio.run(main())