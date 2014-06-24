from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from forms import CreateInvoiceForm
import requests
import json
import hmac
import time
import base64
import hashlib
import os
from decimal import Decimal

def create(request):
    error = None
    if request.method == 'POST': 
        form = CreateInvoiceForm(request.POST) 
        if form.is_valid():
            url = "http://{yellow_server}/api/invoice/".format(yellow_server=os.environ["YELLOW_SERVER"])
            payload= { 'base_price' : str(form.cleaned_data['amount'].quantize(Decimal("0.01"))), 
                       'base_ccy' : form.cleaned_data['currency'],
                       'callback' : "{host}/ipn/".format(host=os.environ["ROOT_URL"])}
            body = json.dumps(payload)
            print body
            credentials = _credentials(url, body)
            headers = {'content-type': 'application/json',
                       'API-Key': credentials[0],
                       'API-Nonce' : credentials[1],
                       'API-Sign' : credentials[2]}
            print headers
            r = requests.post(url,
                              data=body,
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
    
@csrf_exempt
def ipn(request):
    print "IPN"
    print request.POST
    return HttpResponse()
    
def _credentials(url, body):
    api_key = os.environ.get("YELLOW_KEY", "")
    api_secret = os.environ.get("YELLOW_SECRET", "")
    nonce = int(time.time() * 1000)
    message = str(nonce) + url + body
    h = hmac.new(api_secret,
                 message,
                 hashlib.sha256)
    signature = h.hexdigest()
    
    return (api_key, nonce, signature)

