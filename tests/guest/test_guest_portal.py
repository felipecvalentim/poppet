''' Tests to check guest functions

'''

import sys

from flask import current_app
from sqlalchemy import and_,or_

from unifispot.guest.models import Guest,Device,Guestsession,Guesttrack
from unifispot.client.models import Wifisite,Landingpage
from unifispot.models import db
import time

from unifispot.const import *

def test_index_200(session):
    """Makes sure the front page returns HTTP 404.

        A very basic test, to check client page is not accessable directly
    """
    assert '404 NOT FOUND' == current_app.test_client().get('/guest/').status

def test_guest_invalid_values(session):
    # print "sleep 20"
  
    #test for all parameters (id and ap_mac) given by coming user
    assert '404 NOT FOUND' == current_app.test_client().get('/guest/s/site1/').status
    assert '404 NOT FOUND' == current_app.test_client().get('/guest/s/site1/?ap=00:01:00:00:00:11').status
    assert '404 NOT FOUND' == current_app.test_client().get('/guest/s/site1/?id=00:de:ad:be:ef:ca').status
    assert '404 NOT FOUND' == current_app.test_client().get('/guest/s/error/?id=00:de:ad:be:ef:ca&ap=00:01:00:00:00:11').status



    
    
    
    
    
    
