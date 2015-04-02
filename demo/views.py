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
import yellow
from decimal import Decimal

# This file contains a simple exampls for how a merchant might communicate
# with Yellow as part of their shopping cart. There are three functions:
# 'create': create an invoice
# 'ipn': respond to Instant Payment Notification requests
# 'get_signature': sign a request so it will be accepted by Yellow

def create(request):
    ''' Fabricated example that prompts a user for a national currency base
        price and creates the corresponding BTC invoice. A non-demo site would
        likely calculate the base price based on the value of the current
        shopping cart.'''
    error = None
    if request.method == 'POST':
        # Load base price from the user-POSTed form
        form = CreateInvoiceForm(request.POST)
        if form.is_valid():

            api_key = os.environ["API_KEY"]
            api_secret = os.environ["API_SECRET"]
            base_ccy = form.cleaned_data['currency']
            base_price = str(form.cleaned_data['amount'].quantize(Decimal("0.01")))
            callback = "{host}/ipn/".format(host=os.environ["DEMO_HOST"])

            try:
                response = yellow.create_invoice(api_key, api_secret, base_ccy, base_price, callback)
                # At this point the demo just displays the embedded invoice
                # widget. A non-demo site might also open a order in an
                # Order Management System and attach the returned invoice
                # id.
                
                fullscreen = "&full=1" if form.cleaned_data['fullscreen'] else "&full=0"           
                data = response.json()
                context = { 'url' : data['url'] + fullscreen,
                            'yellow_server' : "https://" + os.environ.get("YELLOW_SERVER", "api.yellowpay.co")}
                return render_to_response('demo/invoice.html', context)
            except yellow.YellowApiError as e:
                error = e.message

    return render(request, 'demo/create.html', {
        'form': CreateInvoiceForm(),
        'error': error
    })

def success(request):
    return render(request, 'demo/success.html', {})


@csrf_exempt # No CSRF token is needed or expected
def ipn(request):
    ''' Entry point for the IPN callback. An example approach would be to:
        1. Grab the invoice id and status from the POST payload
        2. Query the order management system for an order matching the invoice
        3a. If the status is 'unconfirmed' flag the order as
            'pending confirmation' and redirect the customer to an order
            complete page
        3b. If the status is 'paid' flag th order as 'complete' and ship the
            the product
    '''

    api_secret = os.environ["API_SECRET"]
    host_url = "{host}/ipn/".format(host=os.environ["DEMO_HOST"])

    verified = yellow.verify_ipn(api_secret, host_url, request)


    if not verified:
        # If signatures are not the same, that means it could be a malicious request:
        # reject it.
        return HttpResponse(status=403)


    payload = json.loads(request.body)
    invoice = payload.get("id", None)
    status = payload.get("status", None)
    if (None == invoice or None == status):
        # This should never happen (we'll always include an invoice id and
        # status), but if it does responding with a 400 will alert us to a
        # problem.
        return HttpResponse(status=400)

    print "Querying Order Management System for order matching invoice id %s" % invoice

    if 'authorizing' == status:
        print "Order is 'pending confirmation', redirecting customer to order complete page."
    elif 'paid' == status:
        print "Order is 'complete', shipping product to customer."

    return HttpResponse()
