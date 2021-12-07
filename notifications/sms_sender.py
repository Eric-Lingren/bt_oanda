from twilio.rest import Client
from __config__ import (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER)


def send_sms(msg):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN) 
    message = client.messages.create( from_=TWILIO_FROM_NUMBER,  to='+18017077067', body=msg ) 