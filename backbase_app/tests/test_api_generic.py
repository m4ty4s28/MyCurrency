import pytest
import re
from unittest.mock import AsyncMock, patch
from aioresponses import aioresponses
from django.utils import timezone

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backbase_project.settings')

import django
django.setup()

from asgiref.sync import sync_to_async

from backbase_app.api.generic_api import GenericAPI, get_provider_exchange, get_all_providers
from backbase_app.models import ProviderExchange

@pytest.fixture
def provider(db):
    return ProviderExchange.objects.create(id_name="TestProvider", activated=True, priority=1)

@pytest.fixture
def generic_api():
    return GenericAPI()

@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_get_provider_exchange(provider):
    provider_exchange = await get_provider_exchange()
    assert provider_exchange is not None
    assert provider_exchange.id_name == "TestProvider"

@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_get_all_providers(provider):
    providers = await get_all_providers()
    assert len(providers) == 1
    assert "TestProvider" in providers

@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_get_currency_rates_list(generic_api):
    start_date = "2025-03-01"
    end_date = "2025-03-05"
    base = "USD"
    symbols = "EUR, GBP"
    
    data = await generic_api.get_currency_rates_list(start_date, end_date, base, symbols)
    
    assert isinstance(data, dict)
    assert all(isinstance(date, str) for date in data.keys())

@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_get_convert_amount(generic_api):
    currency_base = "USD"
    currency_to_convert = "EUR"
    amount = 100
    
    data = await generic_api.get_convert_amount(currency_base, currency_to_convert, amount)
    
    assert isinstance(data, dict)
    assert "value" in data
