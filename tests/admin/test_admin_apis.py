''' Tests to check Admin API functions

'''

import sys
import pytest
from flask import current_app,url_for
from sqlalchemy import and_,or_
from flask.ext.security import current_user
from unifispot.guest.models import Guest,Device,Guestsession,Guesttrack
from unifispot.models import db
import time,uuid

from unifispot.admin.forms import SettingsForm,UserForm
from unifispot.admin.models import Admin
from unifispot.client.models import Client,Wifisite
from unifispot.const import *
from tests.helpers.api import check_api_anonymous_user_not_allowed,check_api_user_type_not_allowed,check_api_get,check_api_get_error
from tests.helpers.api import check_api_post,check_api_post_error,check_api_delete,check_api_delete_error,check_api_get_datatable
from tests.helpers.api import check_api_post_mandatory_fields_check

settings = {'unifi_server':'127.0.0.1','unifi_user':'ubnt','unifi_pass':'ubnt','id':1}





def test_settings_api_anonymous_user(session):
    '''Setting API calls by Non Logged in User'''  
    check_api_anonymous_user_not_allowed(url_for('admin.settings_api'))

def test_settings_api_client_user(session,client1_logged):
    '''Setting API calls by Client User'''   
    check_api_user_type_not_allowed(url_for('admin.settings_api'))

def test_settings_api_admin_get(session,admin1_logged):
    '''Setting API get call by Admin'''
    #call get without ID
    check_api_get(url_for('admin.settings_api'),
                    settings)

    #call get with ID
    check_api_get(url_for('admin.settings_api',id=10),
                    settings)

def test_settings_api_admin_post_error(session,admin1_logged):
    '''Setting API POST call by Admin'''
    new_settings = dict(settings)

    #post empty form
    check_api_post_mandatory_fields_check(url_for('admin.settings_api'),
                ['unifi_server','unifi_pass','unifi_user'],SettingsForm)


def test_settings_api_admin_post(session,admin1_logged):
    '''Setting API POST call by Admin'''
    new_settings = {'unifi_server':'192.168.1.1','unifi_user':'ubntq','unifi_pass':'ubnta','id':1}
    #post  form
    check_api_post(url_for('admin.settings_api'),
                {'unifi_server':'192.168.1.1','unifi_user':'ubntq','unifi_pass':'ubnta'})
    #retrieve same and verify
    check_api_get(url_for('admin.settings_api'),
                    new_settings)

def test_settings_api_admin_delete(session,admin1_logged):
    '''Setting API Delete call by Admin'''
    result = current_app.test_client.delete(url_for('admin.settings_api',id=1),follow_redirects=True).json   
    assert 0 == result['status'], 'Status is not 0 when calling API DELTE Settings'    
    assert 'Not Allowed' == result['msg'], 'Msg  is not Not Allowed when calling API DELTE Settings'    


def test_admin_api_anonymous_user(session):
    '''Admin API calls by Non Logged in User'''  
    check_api_anonymous_user_not_allowed(url_for('admin.admin_api'))

def test_admin_api_client_user(session,client1_logged):
    '''Admin API calls by Client User'''   
    check_api_user_type_not_allowed(url_for('admin.admin_api'))

def test_admin_api_admin_get(session,admin1_logged):
    '''Admin API get call by Admin'''
    #call get without ID, returns datatble
    check_api_get_datatable(url_for('admin.admin_api'),2)
    #call get on self id
    check_api_get(url_for('admin.admin_api',id=1))
    #call get on  id of another admin on same account
    check_api_get(url_for('admin.admin_api',id=2))

    #call get with ID of admin in another account
    check_api_get_error(url_for('admin.admin_api',id=10),'Not Authorized')

def test_admin_api_admin_post_error(session,admin1_logged):
    '''Admin API post call by Admin'''
    #post empty form
    check_api_post_mandatory_fields_check(url_for('admin.admin_api'),
                ['email','displayname'],UserForm)

    #post with passwords not matching
    assert "Error in the Password field - Entered passwords didn't match </br>" == check_api_post_error(url_for('admin.admin_api'),
                {'email':'agsdh@hasj.com','displayname':'sdghadg','password':'ahsjdhaj'})

    #post with email already exists
    assert "Value already exists in the database" == check_api_post_error(url_for('admin.admin_api'),
                {'email':'admin1@admin.com','displayname':'sdghadg','password':'ahsjdhaj','repassword':'ahsjdhaj'})


def test_admin_api_admin_post(session,admin1_logged):
    '''Admin API post call by Admin'''   
    #successful new admin creation
    check_api_post(url_for('admin.admin_api'),
                {'email':'agsdh@hasj.com','displayname':'sdghadg','password':'ahsjdhaj','repassword':'ahsjdhaj'})

    new_admin = Admin.query.filter_by(email='agsdh@hasj.com').first()
    assert isinstance(new_admin,Admin),'Admin post is not successful'

    #call get without ID, returns datatble
    check_api_get_datatable(url_for('admin.admin_api'),3) 

    check_api_post(url_for('admin.admin_api',id=new_admin.id),
                {'email':'agsdh@adasd.com','displayname':'sdgasdasdhadg','password':'test1234','repassword':'test1234'})

  
def test_admin_api_admin_delete(session,admin1_logged):
    '''Admin API delete call by Admin'''   
    #successful admin deletion
    admin1 = Admin.query.filter_by(email='admin1@admin.com').first()  
    admin2 = Admin.query.filter_by(email='admin2@admin.com').first()  
    check_api_delete(url_for('admin.admin_api',id=admin2.id))
    check_api_delete_error(url_for('admin.admin_api',id=admin1.id))


def test_client_api_anonymous_user(session):
    '''Client API calls by Non Logged in User'''  
    check_api_anonymous_user_not_allowed(url_for('admin.client_api'))

def test_client_api_client_user(session,client1_logged):
    '''Client API calls by Client User'''   
    check_api_user_type_not_allowed(url_for('admin.client_api'))


def test_client_api_admin_get(session,admin1_logged):
    '''Client API get call by Admin'''

    client1 = Client.query.filter_by(email='client1@admin.com').first()
    client2 = Client.query.filter_by(email='client2@admin.com').first()
    #call get without ID, returns datatble
    check_api_get_datatable(url_for('admin.client_api'),2)

    #call get on  id of client on same account
    check_api_get(url_for('admin.client_api',id=client1.id))

    #call get with ID of client in another account
    check_api_get_error(url_for('admin.client_api',id=client2.id),'Not Authorized')

def test_client_api_admin_post_error(session,admin1_logged):
    '''Client API post call by Admin'''
    #post empty form
    check_api_post_mandatory_fields_check(url_for('admin.client_api'),
                ['email','displayname'],UserForm)

    #post with passwords not matching
    assert "Error in the Password field - Entered passwords didn't match </br>" == check_api_post_error(url_for('admin.client_api'),
                {'email':'agsdh@hasj.com','displayname':'sdghadg','password':'ahsjdhaj'})

    #post with email already exists
    assert "Value already exists in the database" == check_api_post_error(url_for('admin.client_api'),
                {'email':'admin1@admin.com','displayname':'sdghadg','password':'ahsjdhaj','repassword':'ahsjdhaj'})

def test_client_api_admin_post(session,admin1_logged):
    '''Client API post call by Admin'''   
    #successful new client creation
    check_api_post(url_for('admin.client_api'),
                {'email':'agsdh@hasj.com','displayname':'sdghadg','password':'ahsjdhaj','repassword':'ahsjdhaj'})

    new_client = Client.query.filter_by(email='agsdh@hasj.com').first()
    assert isinstance(new_client,Client),'Client post is not successful'

    #call get without ID, returns datatble
    check_api_get_datatable(url_for('admin.client_api'),3) 

    check_api_post(url_for('admin.client_api',id=new_client.id),
                {'email':'agsdh@adasd.com','displayname':'sdgasdasdhadg','password':'test1234','repassword':'test1234'})

  


def test_aclient_api_admin_delete(session,admin1_logged):
    '''Client API delete call by Admin'''   
    #successful client deletion

    client1 = Client.query.filter_by(email='client1@admin.com').first()
    client2 = Client.query.filter_by(email='client2@admin.com').first() 
    check_api_delete(url_for('admin.client_api',id=client1.id))
    check_api_delete_error(url_for('admin.client_api',id=client2.id))


def test_user_api_anonymous_user(session):
    '''User API calls by Non Logged in User'''  
    check_api_anonymous_user_not_allowed(url_for('admin.user_api'))


def test_client_api_admin_get(session,admin1_logged):
    '''User API get call by Admin'''

    admin1 = Admin.query.filter_by(email='admin1@admin.com').first()
    #call get without ID, not authorized
    check_api_get_error(url_for('admin.user_api'),'Not Authorized')

    #call get on  self user id
    check_api_get(url_for('admin.user_api',id=admin1.id))

    #call get with ID of client in another account
    check_api_get_error(url_for('admin.user_api',id=5),'Not Authorized')

def test_user_api_admin_post(session,admin1_logged):
    '''USer API post call by Admin''' 
    admin1 = Admin.query.filter_by(email='admin1@admin.com').first()
    
    #post without ID is not allowed
    check_api_post_error(url_for('admin.user_api'),
                {'email':'agsdh@hasj.com','displayname':'sdghadg','password':'ahsjdhaj','repassword':'ahsjdhaj'},'Not Authorized')
    #post with another  ID is not allowed
    check_api_post_error(url_for('admin.user_api',id=5),
                {'email':'agsdh@hasj.com','displayname':'sdghadg','password':'ahsjdhaj','repassword':'ahsjdhaj'},'Not Authorized')

    check_api_post(url_for('admin.user_api',id=admin1.id),
                {'email':'agsdh@adasd.com','displayname':'sdgasdasdhadg','password':'test1234','repassword':'test1234'})


def test_user_api_admin_delete(session,admin1_logged):
    '''Admin API delete call by Admin'''   
    #successful admin deletion
    admin1 = Admin.query.filter_by(email='admin1@admin.com').first()  
    admin2 = Admin.query.filter_by(email='admin2@admin.com').first()  
    check_api_delete_error(url_for('admin.user_api',id=admin1.id))
    check_api_delete_error(url_for('admin.user_api',id=admin2.id))


def test_client_api_client_get(session,client1_logged):
    '''User API get call by Client'''

    client1 = Client.query.filter_by(email='client1@admin.com').first()
    #call get without ID, not authorized
    check_api_get_error(url_for('admin.user_api'),'Not Authorized')

    #call get on  self user id
    check_api_get(url_for('admin.user_api',id=client1.id))

    #call get with ID of client in another account
    check_api_get_error(url_for('admin.user_api',id=5),'Not Authorized')


def test_user_api_client_post(session,client1_logged):
    '''USer API post call by Client''' 
    client1 = Client.query.filter_by(email='client1@admin.com').first()
    
    #post without ID is not allowed
    check_api_post_error(url_for('admin.user_api'),
                {'email':'agsdh@hasj.com','displayname':'sdghadg','password':'ahsjdhaj','repassword':'ahsjdhaj'},'Not Authorized')
    #post with another  ID is not allowed
    check_api_post_error(url_for('admin.user_api',id=5),
                {'email':'agsdh@hasj.com','displayname':'sdghadg','password':'ahsjdhaj','repassword':'ahsjdhaj'},'Not Authorized')

    check_api_post(url_for('admin.user_api',id=client1.id),
                {'email':'agsdh@adasd.com','displayname':'sdgasdasdhadg','password':'test1234','repassword':'test1234'})


def test_ap_api_anonymous_user(session):
    '''Accesspoint API calls by Non Logged in User'''  
    check_api_anonymous_user_not_allowed(url_for('admin.ap_api'))

def test_ap_api_admin_get(session,admin1_logged):
    '''Accesspoint API get call by Admin'''
    site1 = Wifisite.query.filter_by(unifi_id='site1').first()
    site3 = Wifisite.query.filter_by(unifi_id='site3').first()

    #call get without ID, get all sites in account
    data = check_api_get(url_for('admin.ap_api'))
    assert 4 == len(data),'Length of json data returned by AP API is not right'

    #call get on  self user id
    check_api_get(url_for('admin.ap_api',id=site1.id))

    #call get with ID of client in another account
    check_api_get_error(url_for('admin.ap_api',id=site3.id),'Not Authorized')

def test_ap_api_admin_post(session,admin1_logged):
    '''Accesspoint API post call by Admin'''
    site1 = Wifisite.query.filter_by(unifi_id='site1').first()    
    check_api_post_error(url_for('admin.ap_api',id=site1.id),'Not Allowed')

def test_ap_api_admin_delete(session,admin1_logged):
    '''Accesspoint API post call by Admin'''
    site1 = Wifisite.query.filter_by(unifi_id='site1').first()    
    check_api_delete_error(url_for('admin.ap_api',id=site1.id),'Not Allowed')



def test_ap_api_client_get(session,client1_logged):
    '''Accesspoint API get call by Client'''
    site1 = Wifisite.query.filter_by(unifi_id='site1').first()
    site3 = Wifisite.query.filter_by(unifi_id='site3').first()

    #call get without ID, get all sites in account
    data = check_api_get(url_for('admin.ap_api'))
    assert 4 == len(data),'Length of json data returned by AP API is not right'

    #call get on  self user id
    check_api_get(url_for('admin.ap_api',id=site1.id))

    #call get with ID of client in another account
    check_api_get_error(url_for('admin.ap_api',id=site3.id),'Not Authorized')

def test_ap_api_client_post(session,client1_logged):
    '''Accesspoint API post call by Client'''
    site1 = Wifisite.query.filter_by(unifi_id='site1').first()    
    check_api_post_error(url_for('admin.ap_api',id=site1.id),'Not Allowed')

def test_ap_api_client_delete(session,client1_logged):
    '''Accesspoint API post call by Client'''
    site1 = Wifisite.query.filter_by(unifi_id='site1').first()    
    check_api_delete_error(url_for('admin.ap_api',id=site1.id),'Not Allowed')


def test_device_api_anonymous_user(session):
    '''Device API calls by Non Logged in User'''  
    check_api_anonymous_user_not_allowed(url_for('admin.device_api'))

def test_device_api_admin_get(session,admin1_logged):
    '''Device API get call by Admin'''
    site1 = Wifisite.query.filter_by(unifi_id='site1').first()
    site3 = Wifisite.query.filter_by(unifi_id='site3').first()

    
    #call get without ID, get all sites in account
    data = check_api_get(url_for('admin.device_api'))
    assert 3 == len(data),'Length of json data returned by AP API is not right'

    #call get on  self user id
    check_api_get(url_for('admin.device_api',id=site1.id))

    #call get with ID of client in another account
    check_api_get_error(url_for('admin.device_api',id=site3.id),'Not Authorized')

def test_device_api_admin_post(session,admin1_logged):
    '''Device API post call by Admin'''
    site1 = Wifisite.query.filter_by(unifi_id='site1').first()    
    check_api_post_error(url_for('admin.device_api',id=site1.id),'Not Allowed')

def test_device_api_admin_delete(session,admin1_logged):
    '''Device API post call by Admin'''
    site1 = Wifisite.query.filter_by(unifi_id='site1').first()    
    check_api_delete_error(url_for('admin.device_api',id=site1.id),'Not Allowed')


def test_device_api_client_get(session,client1_logged):
    '''Device API get call by Client'''
    site1 = Wifisite.query.filter_by(unifi_id='site1').first()
    site3 = Wifisite.query.filter_by(unifi_id='site3').first()

    #call get without ID, get all sites in account
    data = check_api_get(url_for('admin.device_api'))
    assert 3 == len(data),'Length of json data returned by AP API is not right'

    #call get on  self user id
    check_api_get(url_for('admin.device_api',id=site1.id))

    #call get with ID of client in another account
    check_api_get_error(url_for('admin.device_api',id=site3.id),'Not Authorized')

def test_device_api_client_post(session,client1_logged):
    '''Device API post call by Client'''
    site1 = Wifisite.query.filter_by(unifi_id='site1').first()    
    check_api_post_error(url_for('admin.device_api',id=site1.id),'Not Allowed')

def test_device_api_client_delete(session,client1_logged):
    '''Device API post call by Client'''
    site1 = Wifisite.query.filter_by(unifi_id='site1').first()    
    check_api_delete_error(url_for('admin.device_api',id=site1.id),'Not Allowed')