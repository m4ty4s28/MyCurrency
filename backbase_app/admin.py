from django.contrib import admin
from backbase_app.models import CurrencyExchangeRate, Currency, ProviderExchange
from django.contrib import admin
from django.shortcuts import render
from django.contrib import messages
from django.urls import path
from backbase_app.forms import CurrencyConverterForm

class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'symbol') 
    list_filter = ('symbol',) 
    search_fields = ('code', 'name', 'symbol') 
    ordering = ('code',)

class ProviderExchangeAdmin(admin.ModelAdmin):
    list_display = ('id_name', 'name', 'priority', 'activated') 
    list_filter = ('name',) 
    search_fields = ('name', 'priority',) 
    ordering = ('-priority',) 

class CurrencyConverterAdmin(admin.ModelAdmin):
    list_display = ('id', 'source_currency', 'exchanged_currency', 'valuation_date', 'rate_value') 
    list_filter = ('valuation_date',) 
    search_fields = ('source_currency', 'exchanged_currency') 
    ordering = ('-valuation_date',) 

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("converter/", self.admin_site.admin_view(self.converter_view), name="currency_converter"),
        ]
        return custom_urls + urls

    def converter_view(self, request):
        context = {"form": CurrencyConverterForm()}

        if request.method == "POST":

            form = CurrencyConverterForm(request.POST)

            if form.is_valid():
                base_currency = form.cleaned_data["base_currency"]
                target_currencies = form.cleaned_data["target_currencies"]
                amount = float(form.cleaned_data["amount"])

                target_currencies_list = list(target_currencies.values_list("symbol", flat=True))

                from backbase_app.api.generic_api import GenericAPI
                from backbase_app.api.providers_api import run_asyncio_task

                data_return = {
                    "form": form,
                    "amount": amount,
                    "base_currency": base_currency,
                    "conversions" : {}
                }

                conversions_data = {}

                for target_symbol in target_currencies_list:
                    params = {
                        "currency_base" : base_currency.symbol,
                        "currency_to_convert" : target_symbol,
                        "amount" : amount
                    }

                    generic_api = GenericAPI()
                    data = run_asyncio_task(generic_api.get_convert_amount, base_currency.symbol, target_symbol, amount)
                    conversions_data[params["currency_to_convert"]] = round(float(data["value"]),6)
                    
                data_return["conversions"] = conversions_data
                if data_return:
                    context.update(data_return)
                else:
                    messages.error(request, "Exchange rates could not be obtained.")

        return render(request, "admin/converter.html", context)

admin.site.register(Currency, CurrencyAdmin)
admin.site.register(ProviderExchange, ProviderExchangeAdmin)
admin.site.register(CurrencyExchangeRate, CurrencyConverterAdmin)
