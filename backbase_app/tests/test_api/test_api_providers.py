import pytest
from unittest.mock import AsyncMock, patch, MagicMock

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backbase_project.settings')

import django
django.setup()

from backbase_app.api.providers_api import ProvidersAPI
from backbase_app.external_services.api_mock import MockAPI
from backbase_app.external_services.api_currencybeacon import CurrencyBeaconAPI

@pytest.fixture
def mock_api():
    """Create a mocked MockAPI instance.

    Returns:
        MagicMock: A mocked instance of MockAPI.
    """
    mock = MagicMock(spec=MockAPI)
    mock.get_latest_rates = AsyncMock(return_value={"rates": {"EUR": 1.1, "USD": 1.2}})
    mock.get_historical_rates = AsyncMock(return_value={"rates": {"EUR": 1.05}})
    mock.convert_currency = AsyncMock(return_value={"value": 110})
    mock.get_time_series = AsyncMock(return_value={"2025-03-01": {"EUR": 1.1, "USD": 1.2}})
    return mock

@pytest.fixture
def mock_cb_api():
    """Create a mocked CurrencyBeaconAPI instance.

    Returns:
        MagicMock: A mocked instance of CurrencyBeaconAPI.
    """
    mock = MagicMock(spec=CurrencyBeaconAPI)
    mock.get_latest_rates = AsyncMock(return_value={"rates": {"EUR": 1.15, "USD": 1.25}})
    mock.get_historical_rates = AsyncMock(return_value={"rates": {"EUR": 1.08}})
    mock.convert_currency = AsyncMock(return_value={"value": 115})
    mock.get_time_series = AsyncMock(return_value={"2025-03-01": {"EUR": 1.15, "USD": 1.25}})
    return mock

@pytest.fixture
def providers_api(mock_api, mock_cb_api):
    """Create a ProvidersAPI instance with mocked dependencies.

    Args:
        mock_api: Mocked MockAPI instance.
        mock_cb_api: Mocked CurrencyBeaconAPI instance.

    Returns:
        ProvidersAPI: An instance of ProvidersAPI with mocked dependencies.
    """
    with patch('backbase_app.api.providers_api.MockAPI', return_value=mock_api), \
         patch('backbase_app.api.providers_api.CurrencyBeaconAPI', return_value=mock_cb_api):
        api = ProvidersAPI()
        return api

@pytest.mark.asyncio
@patch("backbase_app.api.providers_api.save_data_rate", new_callable=AsyncMock)
async def test_get_latest_rates_mc(mock_save_data_rate, providers_api):
    """Test the get_latest_rates method of ProvidersAPI with Mock API.

    Args:
        mock_save_data_rate: Mocked function for saving rate data.
        providers_api: Fixture providing a ProvidersAPI instance.

    Tests:
        - Verifies that the method returns correct exchange rates
        - Confirms that save_data_rate is called once
    """
    mock_save_data_rate.return_value = {"rate_value": 1.1}

    result = await providers_api.get_latest_rates("USD", ["EUR"], "MC")

    assert result == {"EUR": 1.1}
    mock_save_data_rate.assert_called_once()

@pytest.mark.asyncio
@patch("backbase_app.api.providers_api.save_data_rate", new_callable=AsyncMock)
async def test_get_latest_rates_cb(mock_save_data_rate, providers_api):
    """Test the get_latest_rates method of ProvidersAPI with CurrencyBeacon API.

    Args:
        mock_save_data_rate: Mocked function for saving rate data.
        providers_api: Fixture providing a ProvidersAPI instance.

    Tests:
        - Verifies that the method returns correct exchange rates
        - Confirms that save_data_rate is called once
    """
    mock_save_data_rate.return_value = {"rate_value": 1.15}

    result = await providers_api.get_latest_rates("USD", ["EUR"], "CB")

    assert result == {"EUR": 1.15}
    mock_save_data_rate.assert_called_once()

@pytest.mark.asyncio
@patch("backbase_app.api.providers_api.save_data_rate", new_callable=AsyncMock)
async def test_get_historical_rates_mc(mock_save_data_rate, providers_api):
    """Test the get_historical_rates method of ProvidersAPI with Mock API.

    Args:
        mock_save_data_rate: Mocked function for saving rate data.
        providers_api: Fixture providing a ProvidersAPI instance.

    Tests:
        - Verifies that the method returns correct historical exchange rates
        - Confirms that save_data_rate is called once
    """
    mock_save_data_rate.return_value = {"rate_value": 1.05}

    result = await providers_api.get_historical_rates("2025-03-01", "USD", ["EUR"], "MC")

    assert result == {"EUR": 1.05}
    mock_save_data_rate.assert_called_once()

@pytest.mark.asyncio
@patch("backbase_app.api.providers_api.save_data_rate", new_callable=AsyncMock)
async def test_get_historical_rates_cb(mock_save_data_rate, providers_api):
    """Test the get_historical_rates method of ProvidersAPI with CurrencyBeacon API.

    Args:
        mock_save_data_rate: Mocked function for saving rate data.
        providers_api: Fixture providing a ProvidersAPI instance.

    Tests:
        - Verifies that the method returns correct historical exchange rates
        - Confirms that save_data_rate is called once
    """
    mock_save_data_rate.return_value = {"rate_value": 1.08}

    result = await providers_api.get_historical_rates("2025-03-01", "USD", ["EUR"], "CB")

    assert result == {"EUR": 1.08}
    mock_save_data_rate.assert_called_once()

@pytest.mark.asyncio
@patch("backbase_app.api.providers_api.save_data_convert", new_callable=AsyncMock)
async def test_convert_currency_mc(mock_save_data_convert, providers_api):
    """Test the convert_currency method of ProvidersAPI with Mock API.

    Args:
        mock_save_data_convert: Mocked function for saving conversion data.
        providers_api: Fixture providing a ProvidersAPI instance.

    Tests:
        - Verifies that the method returns correct converted amount
        - Confirms that save_data_convert is called once
    """
    mock_save_data_convert.return_value = None

    result = await providers_api.convert_currency("USD", "EUR", 100, "MC")

    assert result == {"value": 110}
    mock_save_data_convert.assert_called_once()

@pytest.mark.asyncio
@patch("backbase_app.api.providers_api.save_data_convert", new_callable=AsyncMock)
async def test_convert_currency_cb(mock_save_data_convert, providers_api):
    """Test the convert_currency method of ProvidersAPI with CurrencyBeacon API.

    Args:
        mock_save_data_convert: Mocked function for saving conversion data.
        providers_api: Fixture providing a ProvidersAPI instance.

    Tests:
        - Verifies that the method returns correct converted amount
        - Confirms that save_data_convert is called once
    """
    mock_save_data_convert.return_value = None

    result = await providers_api.convert_currency("USD", "EUR", 100, "CB")

    assert result == {"value": 115}
    mock_save_data_convert.assert_called_once()

@pytest.mark.asyncio
@patch("backbase_app.api.providers_api.save_data_time_series", new_callable=AsyncMock)
async def test_get_time_series_mc(mock_save_data_time_series, providers_api):
    """Test the get_time_series method of ProvidersAPI with Mock API.

    Args:
        mock_save_data_time_series: Mocked function for saving time series data.
        providers_api: Fixture providing a ProvidersAPI instance.

    Tests:
        - Verifies that the method returns correct time series data
        - Confirms that save_data_time_series is called once
    """
    mock_save_data_time_series.return_value = None

    result = await providers_api.get_time_series("2025-03-01", "2025-03-01", "USD", ["EUR"], "MC")

    assert result == {"2025-03-01": {"EUR": 1.1, "USD": 1.2}}
    mock_save_data_time_series.assert_called_once()

@pytest.mark.asyncio
@patch("backbase_app.api.providers_api.save_data_time_series", new_callable=AsyncMock)
async def test_get_time_series_cb(mock_save_data_time_series, providers_api):
    """Test the get_time_series method of ProvidersAPI with CurrencyBeacon API.

    Args:
        mock_save_data_time_series: Mocked function for saving time series data.
        providers_api: Fixture providing a ProvidersAPI instance.

    Tests:
        - Verifies that the method returns correct time series data
        - Confirms that save_data_time_series is called once
    """
    mock_save_data_time_series.return_value = None

    result = await providers_api.get_time_series("2025-03-01", "2025-03-01", "USD", ["EUR"], "CB")

    assert result == {"2025-03-01": {"EUR": 1.15, "USD": 1.25}}
    mock_save_data_time_series.assert_called_once()
