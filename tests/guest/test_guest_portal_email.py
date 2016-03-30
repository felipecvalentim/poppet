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


def test_email_login1(session):
    '''Email login with invalid parameters and authorized device
    
    '''
    device_mac      = '00:de:ad:be:ef:da'
    ap_mac          = '00:22:00:00:00:01'
    site            = Wifisite.query.filter_by(unifi_id='site3').first() 
   
    #invalid track ID
    assert '404 NOT FOUND' == current_app.test_client().get('/guest/email/guest/67yte7ey51wy167w2816i2351835').status

    #test valid trackid but no session
    track_id = str(uuid.uuid4())
    guest_track = Guesttrack(ap_mac=ap_mac,device_mac=device_mac,site=site,state=GUESTRACK_INIT,orig_url='',track_id=track_id)
    session.add(guest_track)
    session.commit()
    assert '404 NOT FOUND' == current_app.test_client().get('/guest/email/check/%s'%track_id).status
    #create session but no device
    guest_session = Guestsession(mac=device_mac,state=SESSION_INIT,site=site)
    session.add(guest_session)
    site.sessions.append(guest_session)
    guest_track.session = guest_session
    guest_session.guesttracks.append(guest_track)
    guest_track.state = GUESTRACK_SESSION    
    session.commit()
    assert '404 NOT FOUND' == current_app.test_client().get('/guest/email/guest/%s'%track_id).status
    #with session and authorized device
    guest_device = Device(mac=device_mac,site=site,state=DEVICE_AUTH)
    site.devices.append(guest_device)
    session.add(guest_device)
    guest_device.sessions.append(guest_session) 
    session.commit()
    assert '/guest/auth/guest/%s'%track_id in current_app.test_client().get('/guest/email/guest/%s'%track_id).data
    assert guest_session.state == SESSION_AUTHORIZED
    assert   guest_track.state   == GUESTRACK_SOCIAL_PREAUTH

def test_email_login2(session):
    '''Email login with invalid parameters and non  authorized device
    
    '''
    device_mac      = '00:de:ad:be:ef:df'
    ap_mac          = '00:22:00:00:00:01'
    site            = Wifisite.query.filter_by(unifi_id='site3').first() 
   
    #invalid track ID
    assert '404 NOT FOUND' == current_app.test_client().get('/guest/email/guest/67yte7ey51wy167w2816i2351835').status

    #test valid trackid but no session
    track_id = str(uuid.uuid4())
    guest_track = Guesttrack(ap_mac=ap_mac,device_mac=device_mac,site=site,state=GUESTRACK_INIT,orig_url='',track_id=track_id)
    session.add(guest_track)
    session.commit()
    assert '404 NOT FOUND' == current_app.test_client().get('/guest/email/check/%s'%track_id).status
    #create session but no device
    guest_session = Guestsession(mac=device_mac,state=SESSION_INIT,site=site)
    session.add(guest_session)
    site.sessions.append(guest_session)
    guest_track.session = guest_session
    guest_session.guesttracks.append(guest_track)
    guest_track.state = GUESTRACK_SESSION    
    session.commit()
    assert '404 NOT FOUND' == current_app.test_client().get('/guest/email/guest/%s'%track_id).status
    #with session and authorized device
    guest_device = Device(mac=device_mac,site=site,state=DEVICE_INIT)
    site.devices.append(guest_device)
    session.add(guest_device)
    guest_device.sessions.append(guest_session) 
    session.commit()
    assert '200 OK' == current_app.test_client().get('/guest/email/guest/%s'%track_id).status
    #post data
    form_data = {'firstname':'First Name','email':"email@emailid.com",'lastname':'Last Name'}
    #incomplete data
    assert '302 FOUND' == current_app.test_client().post('/guest/email/guest/%s'%track_id,data=form_data).status    
    #invalid
    form_data['phonenumber'] ='+1234567890'
    form_data['email'] ='not email'
    assert '302 FOUND' == current_app.test_client().post('/guest/email/guest/%s'%track_id,data=form_data).status    
    #valid data
    form_data['email'] ='email@emailid.com'
    assert '/guest/auth/guest/%s'%track_id in current_app.test_client().post('/guest/email/guest/%s'%track_id,data=form_data).data
    assert   guest_session.state == SESSION_AUTHORIZED
    assert   guest_track.state   == GUESTRACK_NEW_AUTH
    assert   guest_device.state  == DEVICE_AUTH
    guest_entry = Guest.query.filter_by().first()
    assert guest_entry.firstname == 'First Name'
    assert guest_entry.lastname == 'Last Name'
    assert guest_entry.email == 'email@emailid.com'
    assert guest_entry.phonenumber == '+1234567890'