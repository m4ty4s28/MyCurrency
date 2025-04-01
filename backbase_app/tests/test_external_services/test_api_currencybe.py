import pytest
from aioresponses import aioresponses

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backbase_project.settings')

import django
django.setup()
import re
from backbase_app.external_services.api_currencybeacon import CurrencyBeaconAPI

@pytest.mark.asyncio
async def test_get_latest_rates():
    api = CurrencyBeaconAPI()
    symbols = ['EUR', 'GBP']
    
    mock_response = {"response": {"base": "USD", "rates": {"EUR": 0.85, "GBP": 0.75}}}
    
    with aioresponses() as m:
        m.get(re.compile(r".*latest.*"), payload=mock_response)
        response = await api.get_latest_rates(base='USD', symbols=symbols)
    
    assert response['base'] == 'USD'
    assert response['rates']['EUR'] == 0.85
    assert response['rates']['GBP'] == 0.75

@pytest.mark.asyncio
async def test_convert_currency():
    api = CurrencyBeaconAPI()
    
    mock_response = {"response": {"from": "USD", "to": "EUR", "amount": 100, "value": 85.0}}
    
    with aioresponses() as m:
        m.get(re.compile(r".*convert.*"), payload=mock_response)
        response = await api.convert_currency('USD', 'EUR', 100)
    
    assert response['from'] == 'USD'
    assert response['to'] == 'EUR'
    assert response['amount'] == 100
    assert response['value'] == 85.0

@pytest.mark.asyncio
async def test_get_historical_rates():
    api = CurrencyBeaconAPI()
    
    mock_response = {"response": {"date": "2025-03-01", "base": "USD", "rates": {"EUR": 0.85, "GBP": 0.75}}}
    
    with aioresponses() as m:
        m.get(re.compile(r".*historical.*"), payload=mock_response)
        response = await api.get_historical_rates('2025-03-01', base='USD', symbols=['EUR', 'GBP'])
    
    assert response['date'] == '2025-03-01'
    assert response['base'] == 'USD'
    assert response['rates']['EUR'] == 0.85
    assert response['rates']['GBP'] == 0.75

@pytest.mark.asyncio
async def test_get_time_series():
    api = CurrencyBeaconAPI()
    
    mock_response = {"response": {"2025-03-01": {"EUR": 0.85, "GBP": 0.75}, "2025-03-02": {"EUR": 0.86, "GBP": 0.76}}}
    
    with aioresponses() as m:
        m.get(re.compile(r".*timeseries.*"), payload=mock_response)
        response = await api.get_time_series('2025-03-01', '2025-03-02', base='USD', symbols=['EUR', 'GBP'])
    
    assert '2025-03-01' in response
    assert response['2025-03-01']['EUR'] == 0.85
    assert response['2025-03-02']['GBP'] == 0.76