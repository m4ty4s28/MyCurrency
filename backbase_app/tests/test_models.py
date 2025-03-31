from django.test import TestCase
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backbase_project.settings')

import django
django.setup()
from backbase_app.models import Currency, CurrencyExchangeRate, ProviderExchange
from datetime import date
from decimal import Decimal

class CurrencyModelTest(TestCase):
    def setUp(self):
        self.currency = Currency.objects.create(code='123456789', name='US Dollar', symbol='USD')

    def test_currency_creation(self):
        self.assertEqual(self.currency.code, '123456789')
        self.assertEqual(self.currency.name, 'US Dollar')
        self.assertEqual(self.currency.symbol, 'USD')

    def test_currency_str(self):
        self.assertEqual(str(self.currency), 'USD')

class CurrencyExchangeRateModelTest(TestCase):
    def setUp(self):
        self.usd = Currency.objects.create(code='123456789', name='US Dollar', symbol='USD')
        self.eur = Currency.objects.create(code='1234567890', name='Euro', symbol='EUR')
        self.exchange_rate = CurrencyExchangeRate.objects.create(
            source_currency=self.usd,
            exchanged_currency=self.eur,
            valuation_date=date.today(),
            rate_value=Decimal("0.85")
        )

    def test_exchange_rate_creation(self):
        self.assertEqual(self.exchange_rate.source_currency, self.usd)
        self.assertEqual(self.exchange_rate.exchanged_currency, self.eur)
        self.assertEqual(self.exchange_rate.rate_value, Decimal("0.85"))

    def test_exchange_rate_str(self):
        self.assertEqual(str(self.exchange_rate), "USD - EUR")

class ProviderExchangeModelTest(TestCase):
    def setUp(self):
        self.provider = ProviderExchange.objects.create(id_name='PROV1', name='Provider One', priority=10, activated=True)

    def test_provider_creation(self):
        self.assertEqual(self.provider.id_name, 'PROV1')
        self.assertEqual(self.provider.name, 'Provider One')
        self.assertEqual(self.provider.priority, 10)
        self.assertTrue(self.provider.activated)

    def test_provider_str(self):
        self.assertEqual(str(self.provider), 'Provider One - 10')
