''' Tests to check Admin  functions

'''

import sys

from flask import current_app,url_for
from sqlalchemy import and_,or_

from unifispot.admin.models import Admin
from unifispot.client.models import Client,Wifisite
from unifispot.models import db
import time,uuid

from unifispot.const import *
from tests.helpers.views import check_view_anonymous_user_not_allowed,check_view_user_type_not_allowed,check_view_user_type_allowed
from tests.helpers.views import check_view_user_404,check_view_user_401

def test_admin_view_anonymous_user(session):
    '''Testing admin views as anonymous user 
    
    '''
    site1 = Wifisite.query.filter_by(unifi_id='site1').first()
    site_id = site1.id

    check_view_anonymous_user_not_allowed(url_for('admin.admin_index'))
    check_view_anonymous_user_not_allowed(url_for('admin.admin_settings'))
    check_view_anonymous_user_not_allowed(url_for('admin.admin_site',site_id=site_id))
    check_view_anonymous_user_not_allowed(url_for('admin.admin_landing',site_id=site_id))
    check_view_anonymous_user_not_allowed(url_for('admin.admin_landing_preview',site_id=site_id))
    check_view_anonymous_user_not_allowed(url_for('admin.admin_clients'))
    check_view_anonymous_user_not_allowed(url_for('admin.admin_admins'))
    check_view_anonymous_user_not_allowed(url_for('admin.client_data',site_id=site_id))
    check_view_anonymous_user_not_allowed(url_for('admin.client_vouchers',site_id=site_id))
    check_view_anonymous_user_not_allowed(url_for('admin.client_print',site_id=site_id))
    
def test_admin_view_client_user(session,client1_logged):
    '''Testing admin views as Client user 
    
    '''
    site1 = Wifisite.query.filter_by(unifi_id='site1').first()
    site_id = site1.id

    check_view_user_type_not_allowed(url_for('admin.admin_index'))
    check_view_user_type_not_allowed(url_for('admin.admin_settings'))
    check_view_user_type_not_allowed(url_for('admin.admin_site',site_id=site_id))
    check_view_user_type_not_allowed(url_for('admin.admin_landing',site_id=site_id))
    check_view_user_type_not_allowed(url_for('admin.admin_landing_preview',site_id=site_id))
    check_view_user_type_not_allowed(url_for('admin.admin_clients'))
    check_view_user_type_not_allowed(url_for('admin.admin_admins'))
    check_view_user_type_not_allowed(url_for('admin.client_data',site_id=site_id))
    check_view_user_type_not_allowed(url_for('admin.client_vouchers',site_id=site_id))
    check_view_user_type_not_allowed(url_for('admin.client_print',site_id=site_id))



def test_admin_view_admin_user(session,admin1_logged):
    '''Testing admin views as Admin user 
    
    '''
    site1 = Wifisite.query.filter_by(unifi_id='site1').first()
    site_id = site1.id

    check_view_user_type_allowed(url_for('admin.admin_index'))
    check_view_user_type_allowed(url_for('admin.admin_settings'))
    check_view_user_type_allowed(url_for('admin.admin_site',site_id=site_id))
    check_view_user_type_allowed(url_for('admin.admin_landing',site_id=site_id))
    check_view_user_type_allowed(url_for('admin.admin_landing_preview',site_id=site_id))
    check_view_user_type_allowed(url_for('admin.admin_clients'))
    check_view_user_type_allowed(url_for('admin.admin_admins'))
    check_view_user_type_allowed(url_for('admin.client_data',site_id=site_id))
    check_view_user_type_allowed(url_for('admin.client_vouchers',site_id=site_id))
    check_view_user_type_allowed(url_for('admin.client_print',site_id=site_id))



def test_admin_view_admin_user_invalid_site(session,admin1_logged):
    '''Testing admin views as Admin user with in valid site ids 
    
    '''
    site_id = 100 #( non existing)


    check_view_user_404(url_for('admin.admin_site',site_id=site_id))
    check_view_user_404(url_for('admin.admin_landing',site_id=site_id))
    check_view_user_404(url_for('admin.admin_landing_preview',site_id=site_id))
    check_view_user_404(url_for('admin.client_data',site_id=site_id))
    check_view_user_404(url_for('admin.client_vouchers',site_id=site_id))
    check_view_user_404(url_for('admin.client_print',site_id=site_id))

    #only voucher print does something with site_id, hence ensure wrong site ID produces 401
    site3 = Wifisite.query.filter_by(unifi_id='site3').first()
    check_view_user_401(url_for('admin.client_print',site_id=site3.id))