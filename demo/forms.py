from django import forms

class CreateInvoiceForm(forms.Form):
    currency = forms.ChoiceField(choices=[('USD', 'USD'),
                                          ('AED', 'AED'),
                                          ('BHD', 'BHD'),
                                          ('DZD', 'DZD'),
                                          ('EGP', 'EGP'),
                                          ('IQD', 'IQD'),
                                          ('JOD', 'JOD'),
                                          ('KWD', 'KWD'),
                                          ('LBP', 'LBP'),
                                          ('MAD', 'MAD'),
                                          ('OMR', 'OMR'),
                                          ('QAR', 'QAR'),
                                          ('SAR', 'SAR'),
                                          ('TND', 'TND'),
                                          ])
    amount = forms.DecimalField()
    style = forms.ChoiceField(choices=[('embedded', 'Embedded Cart'),
                                          ('fullscreen', 'Fullscreen Cart'),
                                          ('link', 'Link'),
                                          ])
