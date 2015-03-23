from django import forms

class CreateInvoiceForm(forms.Form):
    currency = forms.ChoiceField(choices=[('USD', 'USD'),
                                          ('AED', 'AED'),
                                          ('BHD', 'BHD'),
                                          ('DZD', 'DZD'),
                                          ('EGP', 'EGP'),
                                          ('JOD', 'JOD'),
                                          ('LBP', 'LBP'),
                                          ('MAD', 'MAD'),
                                          ('OMR', 'OMR'),
                                          ('QAR', 'QAR'),
                                          ('SAR', 'SAR'),
                                          ('TND', 'TND'),
                                          ])
    amount = forms.DecimalField()
