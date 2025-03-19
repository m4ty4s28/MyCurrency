from django.urls import path, include
from rest_framework.routers import DefaultRouter
from backbase_app.views import CurrencyExchangeViewSet

router = DefaultRouter()
router.register(r'currency_exchange', CurrencyExchangeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]