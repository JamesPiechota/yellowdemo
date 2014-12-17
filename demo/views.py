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

# This file contains a simple exampls for how a merchant might communicate
# with Yellow as part of their shopping cart. There are three functions:
# 'create': create an invoice
# 'ipn': respond to Instant Payment Notification requests
# 'get_signature': sign a request so it will be accepted by Yellow

def create(request):
    ''' Fabricated example that prompts a user for USD or AED price and creates
        the corresponding BTC invoice. A non-demo site would likely calculate
        the USD/AED price based on the value of the current shopping cart.'''
    error = None
    if request.method == 'POST': 
        # Load USD/AED price from the user-POSTed form
        form = CreateInvoiceForm(request.POST) 
        if form.is_valid():
            # Yellow API url to create an invoice
            # Note: all Yellow URLs must be 'https' - since Yellow will redirect 
            # http to https, using an http:// URL may cause authentication
            # to fail
            yellow_server = "https://{yellow_server}".format(yellow_server=os.environ["YELLOW_SERVER"])
            url = "{yellow_server}/v1/api/invoice/".format(yellow_server=yellow_server)
            # POST /api/invoice/ expects a base price, currency, and optional
            # callback. 
            # ROOT_URL should refer to a server you control
            payload= { 'base_price' : str(form.cleaned_data['amount'].quantize(Decimal("0.01"))), 
                       'base_ccy' : form.cleaned_data['currency'],
                       'callback' : "{host}/ipn/".format(host=os.environ["ROOT_URL"])}
            if form.cleaned_data['redirect']:
                payload['redirect'] = "{host}/success".format(host=os.environ["ROOT_URL"])
                
            body = json.dumps(payload)
            
            # Calculate the authentication signature to be included in the
            # request header. See get_signature for more information
            
            # Use the number of milliseconds since epoch (i.e.., UNIX time in
            # milliseconds) as the nonce.
            # A nonce prevents an attacker from replaying your request verbatim as
            # we will reject any request that reuses an existing nonce. We will
            # also reject any request that uses an old nonce, so nonce should always
            # increase.
            nonce = int(time.time() * 1000)

            api_key = os.environ.get("YELLOW_KEY", "")

            signature = get_signature(url, body, nonce)
            headers = {'content-type': 'application/json',
                       'API-Key': api_key,
                       'API-Nonce' : nonce,
                       'API-Sign' : signature}

            # POST the request
            r = requests.post(url,
                              data=body,
                              headers=headers,
                              verify=True)
            if 200 == r.status_code:
                # At this point the demo just displays the embedded invoice
                # widget. A non-demo site might also open a order in an
                # Order Management System and attach the returned invoice
                # id.
                data = r.json()
                context = { 'url' : data['url'],
                            'yellow_server' : yellow_server  }
                return render_to_response('demo/invoice.html', context)
            else:
                error = r.text

    return render(request, 'demo/create.html', {
        'form': CreateInvoiceForm(),
        'error': error
    })
    
def success(request):
    return render(request, 'demo/success.html', {}) 
    
def get_signature(url, body, nonce):
    ''' To secure communication between merchant server and Yellow server we
        use a form of HMAC authentication.
        (http://en.wikipedia.org/wiki/Hash-based_message_authentication_code)
        
        When submitting a request to Yellow 3 additional header elements are
        needed:
        API-Key: your public API key, you can get this from your merchant
                 dashboard
        API-Nonce: an ever-increasing number that is different for each request
                   (e.g., current UNIX time in milliseconds)
        API-Sign: an HMAC hash signed with your API secret and converted to
                  hexadecimal. The message to be hahed and signed is the
                  concatenation of the nonce, fully-qualified request URL,
                  and any request parameters.
                       
        This allows us to authenticate the request as coming from you,
        prevents anyone else from modifying or replaying your request, and
        ensures your secret key is never exposed (even in a Heartbleed-type
        scenario where the SSL layer itself is compromised).
        '''
    
    # Load your API secret from environment variables. For security
    # reasons we recommend # storing any sensitive credentials in environment
    # variables as opposed to hardcoding them directly in source code.
    api_secret = os.environ.get("YELLOW_SECRET", "")
    
    # Concatenate the components of the request to be hashed. They should
    # always be concatenated in this order: Nonce, fully-qualified URL
    # (e.g. https://yellowpay.co/api/invoice/), body
    message = str(nonce) + url + body
    
    # Hash and sign the message with your API secret
    h = hmac.new(api_secret,
                 message,
                 hashlib.sha256)
    
    # Convert he signature to hexadecimal
    signature = h.hexdigest()
    
    return signature


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

    secret = os.environ.get("YELLOW_SECRET", "")

    # Yellow signs its requests with same mechanism clients sign their
    # requests to Yellow API. Therefore, the same logic can be used to verify
    # the signature.
    signature = request.META['HTTP_API_SIGN']

    # Nonces, as is described above, is useful against replay attacks. To 
    # implement nonce checks, the merchant application has to store the last
    # nonce received from Yellow and make sure that this nonce is a fresh one
    # with a higher value than the old one.
    #
    # Because this is just a demo application with no database, we're not
    # implementing the nonce checking. Furthermore, the current set of 
    # functionality that is enabled by IPN requests make replay attacks
    # of little value anyway.
    nonce = request.META['HTTP_API_NONCE']
    body = request.body

    # the URL in this case is the merchant IPN URL registered with
    # Yellow when the invoice was created
    url = "{host}/ipn/".format(host=os.environ["ROOT_URL"])

    test_signature = get_signature(url, body, nonce)

    if test_signature != signature:
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


