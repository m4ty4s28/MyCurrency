from django import forms
from .models import Currency

class CurrencyConverterForm(forms.Form):
    base_currency = forms.ModelChoiceField(queryset=Currency.objects.all(), label="Moneda Base")
    #target_currencies = forms.ModelMultipleChoiceField(queryset=Currency.objects.all(), label="Monedas Destino")
    target_currencies = forms.ModelChoiceField(queryset=Currency.objects.all(), label="Monedas Destino")
    amount = forms.DecimalField(max_digits=10, decimal_places=2, label="Cantidad")
