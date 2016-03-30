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


def test_guest_session_bypass_auth1(session):
    '''User who have visited couple of times during the session, visits again after session expiry
    
    '''
    device_mac      = '00:de:ad:be:ef:ca'
    ap_mac          = '00:22:00:00:00:01'
    site            = Wifisite.query.filter_by(unifi_id='site2').first() 
   
    assert '302 FOUND' == current_app.test_client().get('/guest/s/site2/?id=00:de:ad:be:ef:ca&ap=00:22:00:00:00:01').status
    assert '302 FOUND' == current_app.test_client().get('/guest/s/site2/?id=00:de:ad:be:ef:ca&ap=00:22:00:00:00:01').status
    assert '302 FOUND' == current_app.test_client().get('/guest/s/site2/?id=00:de:ad:be:ef:ca&ap=00:22:00:00:00:01').status
    assert '302 FOUND' == current_app.test_client().get('/guest/s/site2/?id=00:de:ad:be:ef:ca&ap=00:22:00:00:00:01').status

    ##-------------Expire the current session for this user-------------------------------------------
    gsession        = Guestsession.query.filter( and_(Guestsession.mac==device_mac,Guestsession.site_id==site.id)).first()   
    gsession.state  = SESSION_EXPIRED
    session.commit()

    assert '302 FOUND' == current_app.test_client().get('/guest/s/site2/?id=00:de:ad:be:ef:ca&ap=00:22:00:00:00:01').status
    
    num_guesttrack  = Guesttrack.query.filter( and_(Guesttrack.site_id==site.id)).count()
    num_session = Guestsession.query.filter( and_(Guestsession.site_id==site.id)).count()
    num_device  = Device.query.filter( and_(Device.site_id==site.id)).count()
    num_guest  = Guest.query.filter( and_(Guest.site_id==site.id)).count()
    
    assert num_guesttrack == 5 ,"Guesttrack entries not equal to the number of visits:%s"%num_guesttrack
    assert num_session == 2 ,"Guestsession entries not equal to the number of sessions"
    assert num_device == 1 ,"Device entries not equal to the number of unique Devices"
    assert num_guest == 1 ,"Guest entries not equal to the number of unique Devices"

    

def test_guest_session_bypass_auth2(session):
    '''Multiple users visit multiple times, some users visit after session expiry as well
    
    '''
    device_mac      = '00:de:ad:be:ef:ca'
    ap_mac          = '00:22:00:00:00:01'
    site            = Wifisite.query.filter_by(unifi_id='site2').first() 
   
    assert '302 FOUND' == current_app.test_client().get('/guest/s/site2/?id=00:de:ad:be:ef:ca&ap=00:22:00:00:00:01').status
    assert '302 FOUND' == current_app.test_client().get('/guest/s/site2/?id=00:de:ad:be:ef:cb&ap=00:22:00:00:00:01').status
    assert '302 FOUND' == current_app.test_client().get('/guest/s/site2/?id=00:de:ad:be:ef:cc&ap=00:22:00:00:00:01').status
    assert '302 FOUND' == current_app.test_client().get('/guest/s/site2/?id=00:de:ad:be:ef:cd&ap=00:22:00:00:00:01').status
    
    assert '302 FOUND' == current_app.test_client().get('/guest/s/site2/?id=00:de:ad:be:ef:ca&ap=00:22:00:00:00:01').status
    assert '302 FOUND' == current_app.test_client().get('/guest/s/site2/?id=00:de:ad:be:ef:cb&ap=00:22:00:00:00:01').status
    assert '302 FOUND' == current_app.test_client().get('/guest/s/site2/?id=00:de:ad:be:ef:cc&ap=00:22:00:00:00:01').status
    assert '302 FOUND' == current_app.test_client().get('/guest/s/site2/?id=00:de:ad:be:ef:cd&ap=00:22:00:00:00:01').status   
    

    ##-------------Expire the current session for this user-------------------------------------------
    gsession        = Guestsession.query.filter( and_(Guestsession.mac==device_mac,Guestsession.site_id==site.id)).first()   
    gsession.state  = SESSION_EXPIRED
    session.commit()

    assert '302 FOUND' == current_app.test_client().get('/guest/s/site2/?id=00:de:ad:be:ef:ca&ap=00:22:00:00:00:01').status
    assert '302 FOUND' == current_app.test_client().get('/guest/s/site2/?id=00:de:ad:be:ef:cb&ap=00:22:00:00:00:01').status
    assert '302 FOUND' == current_app.test_client().get('/guest/s/site2/?id=00:de:ad:be:ef:cc&ap=00:22:00:00:00:01').status
    assert '302 FOUND' == current_app.test_client().get('/guest/s/site2/?id=00:de:ad:be:ef:cd&ap=00:22:00:00:00:01').status
    
    num_guesttrack  = Guesttrack.query.filter( and_(Guesttrack.site_id==site.id)).count()
    num_session = Guestsession.query.filter( and_(Guestsession.site_id==site.id)).count()
    num_device  = Device.query.filter( and_(Device.site_id==site.id)).count()
    num_guest  = Guest.query.filter( and_(Guest.site_id==site.id)).count()
    
    assert num_guesttrack == 12 ,"Guesttrack entries not equal to the number of visits:%s"%num_guesttrack
    assert num_session == 5 ,"Guestsession entries not equal to the number of sessions"
    assert num_device == 4 ,"Device entries not equal to the number of unique Devices"
    assert num_guest == 4 ,"Guest entries not equal to the number of unique Devices"

    
