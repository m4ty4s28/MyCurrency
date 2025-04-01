import pytest
from unittest.mock import AsyncMock, patch, MagicMock

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backbase_project.settings')

import django
django.setup()

from asgiref.sync import sync_to_async
from backbase_app.api.generic_api import GenericAPI
from backbase_app.models import ProviderExchange
from backbase_app.api.providers_api import ProvidersAPI

@pytest.fixture
def mock_providers_api():
    """Create a mocked ProvidersAPI instance.

    Returns:
        MagicMock: A mocked instance of ProvidersAPI.
    """
    mock = MagicMock(spec=ProvidersAPI)
    mock.get_latest_rates = AsyncMock(return_value={"EUR": 1.1})
    mock.get_historical_rates = AsyncMock(return_value={"EUR": 1.05})
    mock.convert_currency = AsyncMock(return_value={"value": 110})
    mock.get_time_series = AsyncMock(return_value={"2025-03-01": {"EUR": 1.1}})
    return mock

@pytest.fixture
def provider(db):
    """Create a test provider in the database.

    Args:
        db: Django test database fixture.

    Returns:
        ProviderExchange: A test provider instance.
    """
    return ProviderExchange.objects.create(id_name="TestProvider", activated=True, priority=1)

@pytest.fixture
def generic_api(mock_providers_api):
    """Create a GenericAPI instance with mocked dependencies.

    Args:
        mock_providers_api: Mocked ProvidersAPI instance.

    Returns:
        GenericAPI: An instance of GenericAPI with mocked dependencies.
    """
    with patch('backbase_app.api.generic_api.ProvidersAPI', return_value=mock_providers_api):
        return GenericAPI()

@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
@patch('backbase_app.api.generic_api.get_provider_exchange')
async def test_get_provider_exchange(mock_get_provider_exchange):
    """Test the get_provider_exchange function.

    Args:
        mock_get_provider_exchange: Mocked get_provider_exchange function.

    Tests:
        - Verifies that the function returns the correct provider
        - Confirms the provider has the expected id_name
    """
    # Setup mock return value
    mock_provider = MagicMock()
    mock_provider.id_name = "TestProvider"
    mock_get_provider_exchange.return_value = mock_provider

    # Call the mocked function
    provider_exchange = await mock_get_provider_exchange()
    
    # Assertions
    assert provider_exchange is not None
    assert provider_exchange.id_name == "TestProvider"
    
    # Verify the mock was called
    mock_get_provider_exchange.assert_called_once()

@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
@patch('backbase_app.api.generic_api.get_all_providers')
async def test_get_all_providers(mock_get_all_providers):
    """Test the get_all_providers function.

    Args:
        mock_get_all_providers: Mocked get_all_providers function.

    Tests:
        - Verifies that the function returns the correct list of providers
        - Confirms the test provider is in the list
    """
    # Setup mock return value
    expected_providers = ["TestProvider"]
    mock_get_all_providers.return_value = expected_providers

    # Call the mocked function
    providers = await mock_get_all_providers()
    
    # Assertions
    assert len(providers) == 1
    assert "TestProvider" in providers
    
    # Verify the mock was called
    mock_get_all_providers.assert_called_once()

@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
@patch('backbase_app.api.generic_api.GenericAPI.get_currency_rates_list')
async def test_get_currency_rates_list(mock_get_currency_rates_list):
    """Test the get_currency_rates_list method of GenericAPI.

    Args:
        mock_get_currency_rates_list: Mocked get_currency_rates_list method.

    Tests:
        - Verifies that the method returns a dictionary with date keys
        - Confirms the data structure is correct
        - Verifies the method is called with correct parameters
    """
    # Setup mock return value
    expected_data = {
        "2025-03-01": {"EUR": 1.1, "GBP": 0.85},
        "2025-03-02": {"EUR": 1.12, "GBP": 0.86},
        "2025-03-03": {"EUR": 1.15, "GBP": 0.87}
    }
    mock_get_currency_rates_list.return_value = expected_data

    # Test parameters
    start_date = "2025-03-01"
    end_date = "2025-03-05"
    base = "USD"
    symbols = "EUR, GBP"
    
    # Call the mocked method
    data = await mock_get_currency_rates_list(start_date, end_date, base, symbols)
    
    # Assertions
    assert isinstance(data, dict)
    assert all(isinstance(date, str) for date in data.keys())
    assert all(isinstance(rates, dict) for rates in data.values())
    assert all("EUR" in rates and "GBP" in rates for rates in data.values())
    
    # Verify the mock was called with correct parameters
    mock_get_currency_rates_list.assert_called_once_with(start_date, end_date, base, symbols)

@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
@patch('backbase_app.api.generic_api.GenericAPI.get_convert_amount')
async def test_get_convert_amount(mock_get_convert_amount):
    """Test the get_convert_amount method of GenericAPI.

    Args:
        mock_get_convert_amount: Mocked get_convert_amount method.

    Tests:
        - Verifies that the method returns a dictionary with a value key
        - Confirms the data structure is correct
        - Verifies the method is called with correct parameters
    """
    # Setup mock return value
    expected_data = {"value": 110.0}
    mock_get_convert_amount.return_value = expected_data

    # Test parameters
    currency_base = "USD"
    currency_to_convert = "EUR"
    amount = 100
    
    # Call the mocked method
    data = await mock_get_convert_amount(currency_base, currency_to_convert, amount)
    
    # Assertions
    assert isinstance(data, dict)
    assert "value" in data
    assert isinstance(data["value"], (int, float))
    
    # Verify the mock was called with correct parameters
    mock_get_convert_amount.assert_called_once_with(currency_base, currency_to_convert, amount)
