import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backbase_project.settings')

import django
django.setup()

from backbase_app.external_services.api_mock import MockAPI

@pytest.mark.asyncio
async def test_get_latest_rates():
    api = MockAPI()
    symbols = ['EUR', 'GBP']
    response = await api.get_latest_rates(base='USD', symbols=symbols)
    
    assert response['base'] == 'USD'
    assert 'date' in response
    assert all(symbol in response['rates'] for symbol in symbols)
    
@pytest.mark.asyncio
async def test_convert_currency():
    api = MockAPI()
    from_currency, to_currency, amount = 'USD', 'EUR', 100
    response = await api.convert_currency(from_currency, to_currency, amount)
    
    assert response['from'] == from_currency
    assert response['to'] == to_currency
    assert response['amount'] == amount
    assert 'value' in response
    
@pytest.mark.asyncio
async def test_get_time_series():
    api = MockAPI()
    start_date, end_date = '2025-03-01', '2025-03-05'
    symbols = ['EUR', 'GBP']
    response = await api.get_time_series(start_date, end_date, base='USD', symbols=symbols)
    
    assert isinstance(response, dict)
    assert len(response) > 0
    for date in response:
        assert all(symbol in response[date] for symbol in symbols)
    
@pytest.mark.asyncio
async def test_get_historical_rates():
    api = MockAPI()
    date = '2025-03-01'
    symbols = ['EUR', 'GBP']
    response = await api.get_historical_rates(date, base='USD', symbols=symbols)
    
    assert response['date'] == date
    assert response['base'] == 'USD'
    assert all(symbol in response['rates'] for symbol in symbols)
    
@pytest.mark.asyncio
async def test_get_time_series_invalid_dates():
    api = MockAPI()
    with pytest.raises(ValueError, match="start_date must be less than or equal to end_date"):
        await api.get_time_series('2025-03-10', '2025-03-01', base='USD', symbols=['EUR'])
