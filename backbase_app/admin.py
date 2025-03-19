from django.contrib import admin

from django.contrib import admin
from backbase_app.models import CurrencyExchangeRate, Currency

class CurrencyExchangeRateAdmin(admin.ModelAdmin):
    list_display = ('id', 'source_currency', 'exchanged_currency', 'valuation_date', 'rate_value') 
    list_filter = ('valuation_date',) 
    search_fields = ('source_currency', 'exchanged_currency') 
    ordering = ('valuation_date',) 

class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'symbol') 
    list_filter = ('symbol',) 
    search_fields = ('code', 'name', 'symbol') 
    ordering = ('code',) 

admin.site.register(CurrencyExchangeRate, CurrencyExchangeRateAdmin)
admin.site.register(Currency, CurrencyAdmin)
