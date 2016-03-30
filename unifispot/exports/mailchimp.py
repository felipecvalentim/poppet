from flask import current_app
from requests.auth import HTTPBasicAuth
import requests
import json

def export_to_mailchimp(guest,wifisite):
    if not guest.email:
        current_app.logger.error("Guest ID:%s has no emailID for exporting to mailchimp in site:%s"%(guest.id,wifisite.id))
        return 0

    #incase of mailchimp api_auth_field1 = prefix,api_auth_field2=listID,api_auth_field3=api_key
    url     = 'https://%s.api.mailchimp.com/3.0/lists/%s/members/'%(wifisite.api_auth_field1,wifisite.api_auth_field2)
    data = {
        "email_address": guest.email, 
        "status": "subscribed", 
        "merge_fields": {
            "FNAME": guest.firstname if guest.firstname else '', 
            "LNAME": guest.lastname if guest.lastname else ''
        }
    }      

    response = requests.post(url,data=json.dumps(data),auth=('apikey',wifisite.api_auth_field3))
    if response.status_code == 400:
        #
        current_app.logger.error("Bad request ERROR from mailchimp for guestid:%s possibly duplicate entry"%guest.id)
    else:
        response.raise_for_status()
           
    return 1
