''' Tests to check guest functions

'''

import sys

from flask import current_app,url_for
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


def test_wifisite_api_anonymous_user(session):
    '''Wifisite API calls by Non Logged in User'''  
    check_api_anonymous_user_not_allowed(url_for('client.wifisite_api'))

def test_wifisite_api_client_user_get(session,client1_logged):
    '''Wifisite API get calls by Client'''  


