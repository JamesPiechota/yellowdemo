Yellow Demo
==========

Demo code for creating and monitoring Yellow invoices.

This is a simple Django server with two pages:

1. A page to create an invoice in USD or AED
2. A page to display the embedded invoice widget

*views.py* contains sample code to

1. Create an invoice by issuing an authenticated request to the Yellow servers
2. Monitor a callback url ("IPN" Instant Payment Notification) for changes to the invoice status

This demo server just prints to the terminal when the invoice status changes - a real shopping cart integration would likely update an order management system and redirect customers to an order confirmation page.

Code comments contain additional documentation. For any other questions please email info@yellowpay.co

Thanks for using Yellow!

Setup Instructions
==================

* Create a python virtual environment and activate it
* Install [ngrok](https://ngrok.com) and run it, point it at local port 8080. Make note of the URL ngrok gives you.
* Within the root directory of yellowdemo, type:
```
pip install -r requirements.txt
```
* Source the basic environment setup script:
```
source env.sh
```
* Set up the following environment variables:
```
# Set this to the YellowServer supplied to you by the Yellow team
export YELLOW_SERVER=yolanda-perkins.heroku.com
# Set this to the ngrok URL from above
export ROOT_URL=https://dummy.ngrok.com
# Set this to the yellow API Key and Secret given to you by the Yellow team
export YELLOW_KEY=XXX
export YELLOW_SECRET=XXX
```
* Run the server!
```
python manage.py runserver 127.0.0.1:8080
```
