from django.urls import path, include
from rest_framework.routers import DefaultRouter
from backbase_app.views import CurrencyExchangeViewSet, CurrencyViewSet, get_exchange_rate_data, CurrencyExchangeAPIViewSet

router = DefaultRouter()
router.register(r'currency_exchange', CurrencyExchangeViewSet, basename='currency_exchange')
router.register(r'currency_exchange_api', CurrencyExchangeAPIViewSet, basename='currency_exchange_api')
router.register(r'currency', CurrencyViewSet, basename='currency')

urlpatterns = [
    path('', include(router.urls)),
    path('exchange_rate_data/', get_exchange_rate_data),
]