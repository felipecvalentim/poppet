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
from tests.helpers.api import check_api_anonymous_user_not_allowed,check_api_user_type_not_allowed,check_api_get,check_api_get_error
from tests.helpers.api import check_api_post,check_api_post_error,check_api_delete,check_api_delete_error,check_api_get_datatable
from tests.helpers.api import check_api_post_mandatory_fields_check

default_wifisite = { 'name':'','unifi_id':'default', 'id':'', 'default_landing':'','auth_method':AUTH_TYPE_BYPASS, \
                'fb_page':'https://www.facebook.com/unifyhotspot','auth_fb_like':FACEBOOK_LIKE_OFF,'auth_fb_post':FACEBOOK_POST_OFF,\
                'redirect_method':1,'redirect_url':'','timezone':'UTC','emailformfields':FORM_FIELD_ALL,'fb_app_secret':'','fb_appid':''}

site1= dict(default_wifisite)
site2= dict(default_wifisite)
site3= dict(default_wifisite)

site1.update({'name':'Client1 Site1','unifi_id':'site1','auth_fb_like':2,'auth_fb_post':2,'timezone':"Europe/Copenhagen",'auth_method': AUTH_TYPE_SOCIAL,'id':1,'default_landing':1})
site2.update({'name':'Client2 Site1','unifi_id':'site2','timezone':"Europe/Copenhagen",'auth_method': AUTH_TYPE_BYPASS,'id':2,'default_landing':2})
site3.update({'name':'Client3 Site1','unifi_id':'site3','timezone':"Europe/Copenhagen",'auth_method': AUTH_TYPE_EMAIL,'id':3,'default_landing':3})


default_landingpage = {'name':'default','site_id':None,'logofile':0,'bgfile':0,
            'bgcolor':'#ffffff','headerlink':'','basefont':2,'topbgcolor':'#ffffff',
            'toptextcolor':'','topfont':2,'toptextcont':'','middlebgcolor':'#ffffff',
            'middletextcolor':'','middlefont':2,'bottombgcolor':'#ffffff','bottomtextcolor':'',
            'bottomfont':2,'bottomtextcont':'','footerbgcolor':'#ffffff','footertextcolor':'',
            'footerfont':2,'footertextcont':'','btnbgcolor':'','btntxtcolor':'',
            'btnlinecolor':'','tosfile':0,'copytextcont':''
        }

landing1 = dict(default_landingpage)
landing2 = dict(default_landingpage)
landing3 = dict(default_landingpage)
landing1.update({'site_id':1,'id':1})
landing2.update({'site_id':2,'id':2})
landing3.update({'site_id':3,'id':3})

def test_wifisite_api1(session):
    '''Testing Wifisite API
    
    '''
    global default_wifisite
    global site1
    global site2
    global site3
    site3_1 = dict(site3)

    #test getting all stored sites
    result = current_app.test_client().get('/client/site/api/').json
    assert 1 == result['status']
    assert 3 == len(result['data'])
    assert site1 == result['data'][0]
    assert site2 == result['data'][1]
    assert site3 == result['data'][2]


    #get only one site    
    result = current_app.test_client().get('/client/site/api/2').json
    assert 1 == result['status']   
    assert site2 == result['data']

    #add an item
    test_site = dict(default_wifisite)
    test_site.update({'name':'Clinet4 SIte1','redirect_url':'www.google.com','unifi_id':'blahblah'})
    assert {'id': 4, 'msg': 'Added New Entry for:Site Details into Database', 'status': 1} == current_app.test_client().post('/client/site/api/',data=test_site).json
    test_site.update({'default_landing':4,'id':4})
    result = current_app.test_client().get('/client/site/api/4').json
    assert 1 == result['status']   
    assert test_site == result['data']    

    #modify an item
    site3_1.update({'name':'Client3 Site5435','unifi_id':'site2323','timezone':"Europe/Copenhagen",'auth_method': AUTH_TYPE_BYPASS,'id':3,'default_landing':3,'redirect_url': 'www.unifispot.com'})
    assert { 'msg': 'Updated :Site Details', 'status': 1} == current_app.test_client().post('/client/site/api/3',data=site3_1).json
    result = current_app.test_client().get('/client/site/api/3').json
    assert 1 == result['status']   
    assert site3_1 == result['data']

    #Delete an item
    assert {'status':1,'msg':'Deleted Entry:Site Details from Database'} == current_app.test_client().delete('/client/site/api/3').json
    assert '404 NOT FOUND' == current_app.test_client().get('/client/site/api/3').status
    #check if landing page is deleted
    assert 3 == Landingpage.query.count()
    #test getting all stored sites
    result = current_app.test_client().get('/client/site/api/').json
    assert 1 == result['status']
    assert 3 == len(result['data'])
    assert site1 == result['data'][0]
    assert site2 == result['data'][1]
    assert test_site == result['data'][2]


def test_wifisite_api2(session):
    ''' Test Wifisite invalid API calls

    '''
    #Invalid API requests   
    assert '404 NOT FOUND' == current_app.test_client().get('/client/site/api/20').status
    assert '404 NOT FOUND' == current_app.test_client().post('/client/site/api/20').status
    assert '404 NOT FOUND' == current_app.test_client().delete('/client/site/api/20').status
    assert '405 METHOD NOT ALLOWED' == current_app.test_client().delete('/client/site/api/').status

    #test getting all stored sites
    result = current_app.test_client().get('/client/site/api/').json
    assert 1 == result['status']
    assert 3 == len(result['data'])
    assert site1 == result['data'][0]
    assert site2 == result['data'][1]
    assert site3 == result['data'][2]


def test_landingpage_api1(session):
    '''Testing Landingpage API
    
    '''
    global default_landingpage
    global landing1
    global landing2
    global landing3

    landing1_1 = dict(default_landingpage)


    #test getting all stored landingpages
    result = current_app.test_client().get('/client/site/1/landing/api/').json
    assert 1 == result['status']
    assert 1 == len(result['data'])

    landing1_1.update({'id':4,'site_id':1})
    #add new landing page
    assert {'id': 4, 'msg': 'Added New Entry for:Landing Page into Database', 'status': 1}  == current_app.test_client().post('/client/site/1/landing/api/',data=landing1_1).json

    #get the new landing page and check
    result = current_app.test_client().get('/client/site/1/landing/api/4').json
    assert 1 == result['status']   
    assert landing1_1 == result['data']

    #modify the landing page and check
    landing1_1.update({'toptextcolor':'#ffffff','middlefont':1})
    assert { 'id':4,'msg': 'Updated :Landing Page', 'status': 1}  == current_app.test_client().post('/client/site/1/landing/api/4',data=landing1_1).json
    #get the new landing page and check
    result = current_app.test_client().get('/client/site/1/landing/api/4').json
    assert 1 == result['status']   
    assert landing1_1 == result['data']

    #Delete an item
    assert {'status':1,'msg':'Deleted Entry:Landing Page from Database'} == current_app.test_client().delete('/client/site/1/landing/api/4').json
    assert '404 NOT FOUND' == current_app.test_client().get('/client/site/1/landing/api/4').status
    #test getting all stored landingpages and make sure no alterations happened
    pages = Landingpage.query.all()
    assert [landing1,landing2,landing3] == [ page.to_dict() for page in pages]
    

def test_landingpage_api2(session):
    '''Testing Landingpage API invalid calls
    
    '''
    global default_landingpage
    global landing1
    global landing2
    global landing3

    #test invalid API calls
    assert '404 NOT FOUND' == current_app.test_client().get('/client/site/10/landing/api/').status
    assert '404 NOT FOUND' == current_app.test_client().post('/client/site/10/landing/api/').status
    assert '405 METHOD NOT ALLOWED' == current_app.test_client().delete('/client/site/10/landing/api/').status
    assert '404 NOT FOUND' == current_app.test_client().get('/client/site/landing/api/').status
    assert '404 NOT FOUND' == current_app.test_client().post('/client/site/landing/api/').status
    assert '404 NOT FOUND' == current_app.test_client().delete('/client/site/landing/api/').status


    #test getting all stored landingpages and make sure no alterations happened
    pages = Landingpage.query.all()
    assert [landing1,landing2,landing3] == [page.to_dict() for page in pages]
    #assert landing1 == pages[0].to_dict()

def test_sitefile_api1(session):
    '''Testing sitefile API

    '''
    pass

def test_sitefile_api2(session):
    '''Testing sitefile API against invalid parameters

    '''
    pass



