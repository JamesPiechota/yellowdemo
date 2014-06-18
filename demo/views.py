from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from forms import CreateInvoiceForm
import requests
import json
from decimal import Decimal

def create(request):
    error = None
    if request.method == 'POST': 
        form = CreateInvoiceForm(request.POST) 
        if form.is_valid():
            payload= { 'base_price' : str(form.cleaned_data['amount'].quantize(Decimal("0.01"))), 
                       'base_ccy' : form.cleaned_data['currency'] }
            headers = {'content-type': 'application/json'}
            r = requests.post('http://127.0.0.1:8000/api/invoice/',
                              data=json.dumps(payload),
                              headers=headers)
            if 200 == r.status_code:
                data = r.json()
                context = { 'url' : data['url']  }
                return render_to_response('demo/invoice.html', context)
            else:
                error = r.text

    return render(request, 'demo/create.html', {
        'form': CreateInvoiceForm(),
        'error': error
    })

