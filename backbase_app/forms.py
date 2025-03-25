from django import forms
from .models import Currency

class CurrencyConverterForm(forms.Form):
    base_currency = forms.ModelChoiceField(queryset=Currency.objects.all(), label="Base Currency")
    target_currencies = forms.ModelMultipleChoiceField(queryset=Currency.objects.all(), label="Target Currency")
    amount = forms.DecimalField(max_digits=10, decimal_places=2, label="Amount")