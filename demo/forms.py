from django import forms

class CreateInvoiceForm(forms.Form):
    currency = forms.ChoiceField(choices=[('USD', 'USD'), ('AED', 'AED')])
    amount = forms.DecimalField()
