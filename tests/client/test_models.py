''' Tests to check client models

'''

import sys

from flask import current_app
from sqlalchemy import and_,or_

from unifispot.guest.models import Guest,Device,Guestsession,Guesttrack
from unifispot.client.models import Wifisite,Landingpage,Sitefile,Client
from unifispot.models import db
import time,uuid
import pytest

from unifispot.const import *

@pytest.fixture(scope='function')
def populate_clients():
    #add 50 client elements
    from flask.ext.security.utils import encrypt_password
    from unifispot.superadmin.models import Account
    enc_pass        = encrypt_password('zaqxswcdevfr1')
    account         = Account.query.filter_by(id=3).first()   
    for i in range(50):
        admn = Client(email='abc_client%s@abc.com'%i,password=enc_pass,displayname= "ABC_CLIENT%s"%i)
        admn.account = account
        db.session.add(admn)   

def test_check_admin(session):
    client1 = Client.query.filter_by(email='client1@admin.com').first()
    assert False  == client1.check_admin(), 'Clien.check_admin not returning False'


def test_get_user_type(session):
    client1 = Client.query.filter_by(email='client1@admin.com').first()
    assert ROLE_CLIENT  == client1.get_user_type(), 'Clien.get_user_type not returning ROLE_CLIENT'        

def test_get_admin_id(session):
    client1 = Client.query.filter_by(email='client1@admin.com').first()
    assert NotImplemented  == client1.get_admin_id(), 'Clien.get_admin_id not returning NotImplemented'          

def test_check_client(session):
    client1 = Client.query.filter_by(email='client1@admin.com').first()
    assert True  == client1.check_client(), 'Client.check_cleint not returning True'

def test_to_table_row(session):
    client1 = Client.query.filter_by(email='client1@admin.com').first()

    client_dict  = {'displayname':'client1',
                    'email':'client1@admin.com',
                    'id':client1.id,
                    'account_id':client1.account_id
                }
    assert  client_dict == client1.to_table_row(), 'Client.to_table_row not matching'

def test_to_dict(session):
    client1 = Client.query.filter_by(email='client1@admin.com').first()

    client_dict  = {'displayname':'client1',
                    'email':'client1@admin.com',
                    'id':client1.id,
                    'account_id':client1.account_id
                }
    assert  client_dict == client1.to_dict(), 'Client.to_dict not matching'



def test_search_query1(session,populate_clients):
    '''query without modal_filter and no term'''
    client1 = Client.query.filter_by(email='client1@admin.com').first()

    #
    output = client1.search_query(term=None,sort={ 'column':None})
    assert 53 == output['total'],'Total number of objects  not correct'
    assert 10 == len(output['results']),'Total Displayed number of objects not correct'

def test_search_query2(session,populate_clients):
    '''query without modal_filter and  term'''
    client1 = Client.query.filter_by(email='client1@admin.com').first()
   
    #
    output = client1.search_query(term='ABC',sort={ 'column':None})
    assert 50 == output['total'],'Total number of objects  not correct'
    assert 10 == len(output['results']),'Total Displayed number of objects not correct'

def test_search_query3(session,populate_clients):
    '''query  modal_filter and no term'''
    client1 = Client.query.filter_by(email='client1@admin.com').first()
   
    #
    output = client1.search_query(term=None,sort={ 'column':None},modal_filters={'account_id':3})
    assert 50 == output['total'],'Total number of objects  not correct'
    assert 10 == len(output['results']),'Total Displayed number of objects not correct'

def test_search_query4(session,populate_clients):
    '''query  modal_filter and no term  empty resuls'''
    client1 = Client.query.filter_by(email='client1@admin.com').first()
   
    #
    output = client1.search_query(term=None,sort={ 'column':None},modal_filters={'account_id':4})
    assert 0 == output['total'],'Total number of objects  not correct'
    assert 0 == len(output['results']),'Total Displayed number of objects not correct'

def test_search_query5(session,populate_clients):
    '''query  modal_filter and  term emptry results'''
    client1 = Client.query.filter_by(email='client1@admin.com').first()
   
    #
    output = client1.search_query(term='323232',sort={ 'column':None},modal_filters={'account_id':3})
    assert 0 == output['total'],'Total number of objects  not correct'
    assert 0 == len(output['results']),'Total Displayed number of objects not correct'   

def test_search_query6(session,populate_clients):
    '''query  modal_filter and  term '''
    client1 = Client.query.filter_by(email='client1@admin.com').first()
   
    #query  modal_filter and  term
    output = client1.search_query(term='abc_client1',sort={ 'column':None},modal_filters={'account_id':3})
    assert 11 == output['total'],'Total number of objects  not correct'
    assert 10 == len(output['results']),'Total Displayed number of objects not correct'             
