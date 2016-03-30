''' Tests to check guest functions

'''

import sys

from flask import current_app
from sqlalchemy import and_,or_

from unifispot.guest.models import Guest,Device,Guestsession,Guesttrack
from unifispot.client.models import Wifisite,Landingpage
from unifispot.models import db
import time,uuid

from unifispot.const import *


def test_facebook_login1(session):
    '''Facebook login with invalid parameters and no fb cookies
    
    '''
    device_mac      = '00:de:ad:be:ef:da'
    ap_mac          = '00:22:00:00:00:01'
    site            = Wifisite.query.filter_by(unifi_id='site1').first() 
   
    #invalid track ID
    assert '404 NOT FOUND' == current_app.test_client().get('/guest/facebook/check/67yte7ey51wy167w2816i2351835').status

    #test valid trackid but no session
    track_id = str(uuid.uuid4())
    guest_track = Guesttrack(ap_mac=ap_mac,device_mac=device_mac,site=site,state=GUESTRACK_INIT,orig_url='',track_id=track_id)
    db.session.add(guest_track)
    db.session.commit()
    assert '404 NOT FOUND' == current_app.test_client().get('/guest/facebook/check/%s'%track_id).status
    #create session but no device
    guest_session = Guestsession(mac=device_mac,state=SESSION_INIT,site=site)
    db.session.add(guest_session)
    site.sessions.append(guest_session)
    guest_track.session = guest_session
    guest_session.guesttracks.append(guest_track)
    guest_track.state = GUESTRACK_SESSION    
    db.session.commit()
    assert '404 NOT FOUND' == current_app.test_client().get('/guest/facebook/check/%s'%track_id).status
    #with session and authorized device
    guest_device = Device(mac=device_mac,site=site,state=DEVICE_INIT)
    site.devices.append(guest_device)
    db.session.add(guest_device)
    guest_device.sessions.append(guest_session) 
    db.session.commit()
    #assert '/guest/social/guest/%s'%track_id in current_app.test_client().get('/guest/facebook/check/%s'%track_id).data

def test_facebook_login2(session):
    '''Facebook login with invalid parameters and with fb cookies
    
    '''
    ##------------TODO
    pass