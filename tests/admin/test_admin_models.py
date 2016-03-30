''' Tests for admin.models '''

import sys
import pytest
from flask import current_app
from sqlalchemy import and_,or_

from unifispot.guest.models import Guest,Device,Guestsession,Guesttrack
from unifispot.admin.models import Admin
from unifispot.models import db
import time,uuid

from unifispot.const import *

@pytest.fixture(scope='function')
def populate_admins():
    #add 50 admin elements
    from flask.ext.security.utils import encrypt_password
    from unifispot.superadmin.models import Account
    enc_pass        = encrypt_password('zaqxswcdevfr1')
    account         = Account.query.filter_by(id=3).first()   
    for i in range(50):
        admn = Admin(email='abc_admin%s@abc.com'%i,password=enc_pass,displayname= "ABC_ADMIN%s"%i)
        admn.account = account
        db.session.add(admn)          



def test_check_admin(session):
    admin1 = Admin.query.filter_by(email='admin1@admin.com').first()
    assert True  == admin1.check_admin(), 'Admin.check_admin not returning True'


def test_get_user_type(session):
    admin1 = Admin.query.filter_by(email='admin1@admin.com').first()
    assert ROLE_ADMIN  == admin1.get_user_type(), 'Admin.get_user_type not returning ROLE_ADMIN'        

def test_get_admin_id(session):
    admin1 = Admin.query.filter_by(email='admin1@admin.com').first()
    assert NotImplemented  == admin1.get_admin_id(), 'Admin.get_admin_id not returning NotImplemented'          

def test_check_client(session):
    admin1 = Admin.query.filter_by(email='admin1@admin.com').first()
    assert False  == admin1.check_client(), 'Admin.check_cleint not returning False'

def test_to_table_row(session):
    admin1 = Admin.query.filter_by(email='test1@test.com').first()

    admin_dict  = {'displayname':'TEST Admin1',
                    'email':'test1@test.com',
                    'id':3,
                    'account':'Account2'
                }
    assert  admin_dict == admin1.to_table_row(), 'Admin.to_table_row not matching'

def test_to_dict(session):
    admin1 = Admin.query.filter_by(email='test1@test.com').first()

    admin_dict  = {'displayname':'TEST Admin1',
                    'email':'test1@test.com',
                    'id':3,
                    'account_id':2
                }
    assert  admin_dict == admin1.to_dict(), 'Admin.to_dict not matching'


def test_search_query1(session,populate_admins):
    '''query without modal_filter and no term'''
    admin1 = Admin.query.filter_by(email='test1@test.com').first()

    #
    output = admin1.search_query(term=None,sort={ 'column':None})
    assert 56 == output['total'],'Total number of objects  not correct'
    assert 10 == len(output['results']),'Total Displayed number of objects not correct'

def test_search_query2(session,populate_admins):
    '''query without modal_filter and  term'''
    admin1 = Admin.query.filter_by(email='test1@test.com').first()
   
    #
    output = admin1.search_query(term='test',sort={ 'column':None})
    assert 4 == output['total'],'Total number of objects  not correct'
    assert 4 == len(output['results']),'Total Displayed number of objects not correct'

def test_search_query3(session,populate_admins):
    '''query  modal_filter and no term'''
    admin1 = Admin.query.filter_by(email='test1@test.com').first()
   
    #
    output = admin1.search_query(term=None,sort={ 'column':None},modal_filters={'account_id':3})
    assert 50 == output['total'],'Total number of objects  not correct'
    assert 10 == len(output['results']),'Total Displayed number of objects not correct'

def test_search_query4(session,populate_admins):
    '''query  modal_filter and no term  empty resuls'''
    admin1 = Admin.query.filter_by(email='test1@test.com').first()
   
    #
    output = admin1.search_query(term=None,sort={ 'column':None},modal_filters={'account_id':4})
    assert 0 == output['total'],'Total number of objects  not correct'
    assert 0 == len(output['results']),'Total Displayed number of objects not correct'

def test_search_query5(session,populate_admins):
    '''query  modal_filter and  term emptry results'''
    admin1 = Admin.query.filter_by(email='test1@test.com').first()
   
    #
    output = admin1.search_query(term='test',sort={ 'column':None},modal_filters={'account_id':3})
    assert 0 == output['total'],'Total number of objects  not correct'
    assert 0 == len(output['results']),'Total Displayed number of objects not correct'   

def test_search_query6(session,populate_admins):
    '''query  modal_filter and  term '''
    admin1 = Admin.query.filter_by(email='test1@test.com').first()
   
    #query  modal_filter and  term
    output = admin1.search_query(term='abc_admin1',sort={ 'column':None},modal_filters={'account_id':3})
    assert 11 == output['total'],'Total number of objects  not correct'
    assert 10 == len(output['results']),'Total Displayed number of objects not correct'             
