import pytest
import re
from aioresponses import aioresponses
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backbase_project.settings')

import django
django.setup()

from backbase_app.api.internal_api import InternalAPI

@pytest.mark.asyncio
async def test_get_exchange_rate_data():
    api = InternalAPI()
    
    mock_response = {
        "source_currency": "USD",
        "exchanged_currency": "EUR",
        "valuation_date": "2025-03-31",
        "rate_value": 0.85
    }
    
    with aioresponses() as m:
        m.get(re.compile(r".*currency_exchange_api.*"), payload=mock_response)
        response = await api.get_exchange_rate_data("USD", "EUR", "2025-03-31")
    
    assert response["source_currency"] == "USD"
    assert response["exchanged_currency"] == "EUR"
    assert response["valuation_date"] == "2025-03-31"
    assert response["rate_value"] == 0.85

@pytest.mark.asyncio
async def test_get_currency_rates_list():
    api = InternalAPI()
    
    mock_response = [
        {"valuation_date": "2025-03-30", "exchanged_currency__symbol": "EUR", "rate_value": 0.85},
        {"valuation_date": "2025-03-31", "exchanged_currency__symbol": "EUR", "rate_value": 0.86}
    ]
    
    with aioresponses() as m:
        m.get(re.compile(r".*currency_rates_list_api.*"), payload=mock_response)
        response = await api.get_currency_rates_list("2025-03-30", "2025-03-31", "USD", "EUR")
    
    assert response["2025-03-30"]["EUR"] == 0.85
    assert response["2025-03-31"]["EUR"] == 0.86

@pytest.mark.asyncio
async def test_get_convert_amount():
    api = InternalAPI()
    
    mock_response = {"rate_value": 0.85}
    
    with aioresponses() as m:
        m.get(re.compile(r".*currency_exchange_api.*"), payload=mock_response)
        response = await api.get_convert_amount("USD", "EUR", 100)
    
    assert response["from"] == "USD"
    assert response["to"] == "EUR"
    assert response["amount"] == 100
    assert response["value"] == 85.0  # 100 * 0.85
