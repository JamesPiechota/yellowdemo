yellowdemo
==========

Demo code for creating and monitorying Yellow invoices.

This is a simple Django server with two pages:
1. A page to create an invoice in USD or AED
2. A page with the embedded invoice widget

views.py contains sample code to
1. Create an invoice by issueing an authenticated request to the Yellow servers
2. Monitor a callback url ("IPN" Instant Payment Notification) for changes to the invoice status

This demo server just prints to the terminal when the invoice status changes - a real shopping cart integration would likely update an order management system and redirect customers to an order confirmation page.

Code comments contain additional documentation. For any other questions please email info@yellowpay.co

Thanks for using Yellow!
