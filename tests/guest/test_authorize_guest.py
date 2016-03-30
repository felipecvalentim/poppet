''' Tests to check guest functions

'''

import sys
import uuid
from flask import current_app
from sqlalchemy import and_,or_

from unifispot.guest.models import Guest,Device,Guestsession,Guesttrack
from unifispot.client.models import Wifisite
from unifispot.models import db
import time
import json
from unifispot.const import *
import arrow

device_mac      = '00:de:ad:be:ef:ca'
ap_mac          = '00:22:00:00:00:01'


def test_authorize_guest(session):
    '''Test authorize methods, invalid
    
    '''
    site            = Wifisite.query.filter_by(unifi_id='site2').first() 
    #invalid trackid
    assert '404 NOT FOUND' == current_app.test_client().get('/guest/auth/guest/67yte7ey51wy167w2816i2351835').status
    #test valid trackid but no session
    track_id = str(uuid.uuid4())
    guest_track = Guesttrack(ap_mac=ap_mac,device_mac=device_mac,site=site,state=GUESTRACK_INIT,orig_url='',track_id=track_id)
    db.session.add(guest_track)
    db.session.commit()
    assert '404 NOT FOUND' == current_app.test_client().get('/guest/auth/guest/%s'%track_id).status
    #create session but not authorized
    guest_session = Guestsession(mac=device_mac,state=SESSION_INIT,site=site)
    db.session.add(guest_session)
    site.sessions.append(guest_session)
    guest_track.session = guest_session
    guest_session.guesttracks.append(guest_track)
    guest_track.state = GUESTRACK_SESSION    
    db.session.commit()
    assert '404 NOT FOUND' == current_app.test_client().get('/guest/auth/guest/%s'%track_id).status
    #Create device and authorize session
    guest_device = Device(mac=device_mac,site=site,state=DEVICE_INIT)
    site.devices.append(guest_device)
    db.session.add(guest_device)
    guest_device.sessions.append(guest_session)
    guest_session.state = SESSION_AUTHORIZED
    guest_track.state   = GUESTRACK_NO_AUTH
    guest_device.state  = DEVICE_AUTH    
    db.session.commit()
    assert '302 FOUND' == current_app.test_client().get('/guest/auth/guest/%s'%track_id).status
    #expire the session and try again
    guest_session.expiry = arrow.utcnow().replace(hours=-10).naive
    db.session.commit
    assert '404 NOT FOUND' == current_app.test_client().get('/guest/auth/guest/%s'%track_id).status


def test_temp_authorize_guest(session):
    '''Test authorize methods
    
    '''
    device_mac      = '00:de:ad:be:ef:ca'
    ap_mac          = '00:22:00:00:00:01'
    site            = Wifisite.query.filter_by(unifi_id='site2').first() 

    auth_pass_status = {'status':1,'msg': "DEBUG enabled"}
    auth_fail_status = {'status':0,'msg': "Error"}
    auth_fail_status1 = {'status':0,'msg': "You have already used up temporary logins for today"}


    #invalid trackid
    assert auth_fail_status == current_app.test_client().get('/guest/tempauth/guest/67yte7ey51wy167w2816i2351835').json
    #test valid trackid but no session
    track_id = str(uuid.uuid4())
    guest_track = Guesttrack(ap_mac=ap_mac,device_mac=device_mac,site=site,state=GUESTRACK_INIT,orig_url='',track_id=track_id)
    db.session.add(guest_track)
    db.session.commit()
    assert auth_fail_status == current_app.test_client().get('/guest/tempauth/guest/%s'%track_id).json
    #create session but not authorized
    guest_session = Guestsession(mac=device_mac,state=SESSION_INIT,site=site)
    db.session.add(guest_session)
    site.sessions.append(guest_session)
    guest_track.session = guest_session
    guest_session.guesttracks.append(guest_track)
    guest_track.state = GUESTRACK_SESSION    
    db.session.commit()
    assert auth_fail_status == current_app.test_client().get('/guest/tempauth/guest/%s'%track_id).json

    #Create device and authorize session
    guest_device = Device(mac=device_mac,site=site,state=DEVICE_INIT)
    site.devices.append(guest_device)
    db.session.add(guest_device)
    guest_device.sessions.append(guest_session)
    guest_session.state = SESSION_TEMP_AUTH
    db.session.commit()
    assert auth_pass_status == current_app.test_client().get('/guest/tempauth/guest/%s'%track_id).json
    #test if miss use prevention is working
    for i in range(1,10):
        assert auth_pass_status == current_app.test_client().get('/guest/tempauth/guest/%s'%track_id).json
    assert auth_fail_status1 == current_app.test_client().get('/guest/tempauth/guest/%s'%track_id).json