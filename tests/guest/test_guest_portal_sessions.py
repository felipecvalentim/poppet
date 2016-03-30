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
import arrow

device_mac  = '00:de:ad:be:ef:ca'
ap_mac      = '00:22:00:00:00:01'

def test_guest_session_int1(session):
    '''test if the session is created for this user
    
    '''

    site        = Wifisite.query.filter_by(unifi_id='site2').first()
    assert '200 OK' == current_app.test_client().get('/guest/s/site2/?id=00:de:ad:be:ef:ca&ap=00:22:00:00:00:01').status

    # test if the session is created for this user
    test_session = Guestsession.query.filter( and_(Guestsession.mac==device_mac,Guestsession.site_id==site.id)).first()
    test_device  = Device.query.filter( and_(Device.mac==device_mac,Device.site_id==site.id)).first()
    assert isinstance(test_session, Guestsession), "Session is not created when a new user visits"
    assert isinstance(test_device, Device), "Device is not created when a new user visits"
 
 
def test_guest_session_int2(session):
    '''Same user visiting twice without session expity, shouldn't cause new session creating
    
    '''
    site        = Wifisite.query.filter_by(unifi_id='site2').first()
    
    #
    #
    assert '200 OK' == current_app.test_client().get('/guest/s/site2/?id=00:de:ad:be:ef:ca&ap=00:22:00:00:00:01').status
    time.sleep(1)
    assert '200 OK' == current_app.test_client().get('/guest/s/site2/?id=00:de:ad:be:ef:ca&ap=00:22:00:00:00:01').status
    assert '200 OK' == current_app.test_client().get('/guest/s/site2/?id=00:de:ad:be:ef:ca&ap=00:22:00:00:00:01').status
    assert '200 OK' == current_app.test_client().get('/guest/s/site2/?id=00:de:ad:be:ef:ca&ap=00:22:00:00:00:01').status
    num_session = Guestsession.query.filter( and_(Guestsession.mac==device_mac,Guestsession.site_id==site.id)).count()
    assert num_session == 1 , "User visiting twice without session expiry: Session shouldn't be created twice"
    #
    num_device  = Device.query.filter( and_(Device.mac==device_mac,Device.site_id==site.id)).count()
    assert num_device == 1 , "User visiting twice without session expiry: Device shouldn't be created twice"
    #
    assert 4 == Guesttrack.query.count() , "User visiting  without session expiry: Guesttrack should be created eachtime"


def test_guest_session_int3(session):
    '''Same user visiting twice with session expiry, New session to be created
    
    '''
    site        = Wifisite.query.filter_by(unifi_id='site2').first()    
    #
    #   
    assert '200 OK' == current_app.test_client().get('/guest/s/site2/?id=00:de:ad:be:ef:ca&ap=00:22:00:00:00:01').status
    test_session = Guestsession.query.filter( and_(Guestsession.mac==device_mac,Guestsession.site_id==site.id)).first()   

    test_session.expiry = arrow.utcnow().replace(minutes=-10).naive
    session.commit()
    assert '200 OK' == current_app.test_client().get('/guest/s/site2/?id=00:de:ad:be:ef:ca&ap=00:22:00:00:00:01').status
    #
    num_session = Guestsession.query.filter( and_(Guestsession.mac==device_mac,Guestsession.site_id==site.id)).count()
    assert num_session == 2 , "User visiting twice with session expiry: Session should be created twice"
    #
    num_device  = Device.query.filter( and_(Device.mac==device_mac,Device.site_id==site.id)).count()
    assert num_device == 1 , "User visiting twice with session expiry: Device shouldn't be created twice"
    

def test_guest_session_int4(session):
    '''Same user visiting multiple sites
    
    '''
    site1        = Wifisite.query.filter_by(unifi_id='site1').first() 
    site2        = Wifisite.query.filter_by(unifi_id='site2').first() 
    site3        = Wifisite.query.filter_by(unifi_id='site3').first()

    assert '200 OK' == current_app.test_client().get('/guest/s/site1/?id=00:de:ad:be:ef:ca&ap=00:22:00:00:00:01').status    
    assert '200 OK' == current_app.test_client().get('/guest/s/site1/?id=00:de:ad:be:ef:ca&ap=00:22:00:00:00:01').status    
    assert '200 OK' == current_app.test_client().get('/guest/s/site2/?id=00:de:ad:be:ef:ca&ap=01:22:00:00:00:01').status    
    assert '200 OK' == current_app.test_client().get('/guest/s/site2/?id=00:de:ad:be:ef:ca&ap=01:22:00:00:00:01').status    
    assert '200 OK' == current_app.test_client().get('/guest/s/site3/?id=00:de:ad:be:ef:ca&ap=02:22:00:00:00:01').status   
    assert '200 OK' == current_app.test_client().get('/guest/s/site3/?id=00:de:ad:be:ef:ca&ap=02:22:00:00:00:01').status   

    assert 6 == Guesttrack.query.count(), "Same device visiting 3 sites twice, 6 Guesttrack needed" 
    assert 3 == Guestsession.query.count(), "Same device visiting 3 sites, 3 Guestsession needed" 
    assert 3 == Device.query.count(), "Same device visiting 3 sites, 3 Device needed" 

    #expires one site
    guest_session1 = Guestsession.query.filter( and_(Guestsession.mac==device_mac,Guestsession.site_id==site1.id)).first()
    guest_session2 = Guestsession.query.filter( and_(Guestsession.mac==device_mac,Guestsession.site_id==site2.id)).first()
    guest_session3 = Guestsession.query.filter( and_(Guestsession.mac==device_mac,Guestsession.site_id==site3.id)).first()
    assert isinstance(guest_session1, Guestsession), "Session is not created when a new user visits"
    assert isinstance(guest_session2, Guestsession), "Session is not created when a new user visits"
    assert isinstance(guest_session3, Guestsession), "Session is not created when a new user visits"

    guest_session1.expiry = arrow.utcnow().replace(minutes=-10).naive
    session.commit()   
    assert '200 OK' == current_app.test_client().get('/guest/s/site1/?id=00:de:ad:be:ef:ca&ap=00:22:00:00:00:01').status    
    assert '200 OK' == current_app.test_client().get('/guest/s/site1/?id=00:de:ad:be:ef:ca&ap=00:22:00:00:00:01').status    
    assert '200 OK' == current_app.test_client().get('/guest/s/site2/?id=00:de:ad:be:ef:ca&ap=01:22:00:00:00:01').status    
    assert '200 OK' == current_app.test_client().get('/guest/s/site2/?id=00:de:ad:be:ef:ca&ap=01:22:00:00:00:01').status    
    assert '200 OK' == current_app.test_client().get('/guest/s/site3/?id=00:de:ad:be:ef:ca&ap=02:22:00:00:00:01').status   
    assert '200 OK' == current_app.test_client().get('/guest/s/site3/?id=00:de:ad:be:ef:ca&ap=02:22:00:00:00:01').status 

    assert 12 == Guesttrack.query.count(), "Same device visiting 3 sites twice second time , 12 Guesttrack needed" 
    assert 4 == Guestsession.query.count(), "Only Guestsession in site1 expired hence 4 sessions" 
    assert 3 == Device.query.count(), "Same device visiting 3 sites multiple times, 3 Device needed" 

    #check if all objects are correctly connected.
    guest_session1_new = Guestsession.query.filter( and_(Guestsession.mac==device_mac,Guestsession.site_id==site1.id)).first()
    assert isinstance(guest_session1_new, Guestsession), "Session is not created when a new user visits"





