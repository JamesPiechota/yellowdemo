#!/bin/bash
export DEBUG=1
export DJANGO_PROJECT=yellowdemo
# This is a dummy SECRET_KEY provided for convenience, make sure you change if you
# ever run this on a public facing website
export SECRET_KEY=375e64bf082645951ba9fc1ced1e3f4f
# Set this to the YellowServer supplied to you by the Yellow team
export YELLOW_SERVER=api.yellowpay.co



# Set this to the ngrok https forwarding URL you see in the terminal when you run ngrok
export DEMO_HOST=XXX

# Set this to the yellow API Key and Secret. Get it from your merchant dashboard.
export API_KEY=XXX
export API_SECRET=XXX
