from flask import url_for
from urllib2 import urlopen
import time
import pytest

from unifispot.client.models import Wifisite,Landingpage
from unifispot.const import AUTH_TYPE_ALL,AUTH_TYPE_EMAIL
from unifispot.guest.models import Guest,Device,Guestsession,Guesttrack
from unifispot.models import db
from helpers.utils import get_elements

@pytest.mark.e2e
def test_guest_login_email(browser,session,live_server):
    '''Test to check if landing page is shown as per the auth_method configured'''
    
    site        = Wifisite.query.filter_by(unifi_id='site1').first()
    site_url    = url_for('guest.guest_portal',id='11:22:33:44:55',ap='11:22:33:44:55',site_id='site1',_external=True)
    login_btns  = ['email-select','phone-select','voucher-select','fb-select']
    site.auth_method = AUTH_TYPE_EMAIL
    session.commit()

    live_server.start()
    def set_and_check_auth_type(auth_type,bitmap):
        btns_to_check = {}
        #create result dict for comparison
        for idx, val in enumerate(login_btns):
            btns_to_check[val] = None
            if bitmap[idx]:
                btns_to_check[val] = 1
        btns_seen   = get_elements(browser,site_url,login_btns)   
        time.sleep(3)
        assert btns_seen ==  btns_to_check, 'Configured method :%s expected butons:%s seen:%s'%(auth_type,btns_to_check,btns_seen)

    #configure all authentications

    #btns_seen   = get_elements(browser,site_url,login_btns)
    #assert btns_seen == {'email-select':1,'phone-select':1,'voucher-select':1,'fb-select':1},'Not all buttons are shown when configured with '

    #set_and_check_auth_type(AUTH_TYPE_EMAIL,[1,None,None,None]) 
    browser.get(site_url)
    time.sleep(3)
    #print site_url
    #browser.find_element_by_id('email-select').click()
    time.sleep(35)
