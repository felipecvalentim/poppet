from unifispot.client.models import Wifisite,Landingpage
from unifispot.const import *
from unifispot.models import User

from unifispot.models import user_datastore
from flask.ext.security.utils import encrypt_password
from unifispot.admin.models import Admin
from unifispot.client.models import Client
from unifispot.superadmin.models import Account


def init_data(session):

    account1 = Account(name='Account1')
    account2 = Account(name='Account2')
    account3 = Account(name='Account3')
    account4 = Account(name='Account4')
    account5 = Account(name='Account5')
    session.add(account1)
    session.add(account2)
    session.add(account3)
    session.add(account4)
    session.add(account5)
    ##----------------Add users which will be used always---------
    enc_pass        = encrypt_password('zaqxswcdevfr1')
    admin_user1      = Admin(email='admin1@admin.com',password=enc_pass,displayname= "Admin1",active=1)
    admin_user2      = Admin(email='admin2@admin.com',password=enc_pass,displayname= "Admin2",active=1)
    admin_user3      = Admin(email='test1@test.com',password=enc_pass,displayname= "TEST Admin1",active=1)
    admin_user4      = Admin(email='test2@test.com',password=enc_pass,displayname= "TEST Admin2",active=1)
    admin_user5      = Admin(email='test3@test.com',password=enc_pass,displayname= "TEST Admin3",active=1)
    admin_user6      = Admin(email='test4@test.com',password=enc_pass,displayname= "TEST Admin4",active=1)
    session.add(admin_user1)
    session.add(admin_user2)
    session.add(admin_user3)
    session.add(admin_user4)
    session.add(admin_user5)
    session.add(admin_user6)
    admin_user1.account = account1
    admin_user2.account = account1
    admin_user3.account = account2
    admin_user4.account = account2
    admin_user5.account = account2
    admin_user6.account = account2

    enc_pass        = encrypt_password('zaqxswcdevfr1')
    client_user1      = Client(email='client1@admin.com',password=enc_pass,displayname= "client1",active=1)
    client_user2      = Client(email='client2@admin.com',password=enc_pass,displayname= "client2",active=1)
    client_user3      = Client(email='client3@admin.com',password=enc_pass,displayname= "client2",active=1)
    session.add(client_user1)
    session.add(client_user2)
    session.add(client_user3)
    client_user1.account = account1
    client_user2.account = account2
    client_user3.account = account1



    #
    #------------site1 will be configured with some basic settings for the landing page--
    #Used to test social landing
    site1           = Wifisite(name='Client1 Site1',unifi_id='site1',auth_fb_like=1,timezone="Europe/Copenhagen",auth_method= AUTH_TYPE_ALL)    
    site2           = Wifisite(name='Client1 Site2',unifi_id='site2',timezone="Europe/Copenhagen",auth_method= AUTH_TYPE_ALL)
    site3           = Wifisite(name='Client2 Site1',unifi_id='site3',timezone="Europe/Copenhagen",auth_method= AUTH_TYPE_ALL)
    session.add(site1)
    session.add(site2)
    session.add(site3)
    site1.account   = account1
    site2.account   = account1
    site3.account   = account2
    site1.client    = client_user1
    site2.client    = client_user1
    site3.client    = client_user2
    session.commit()
    
    
     
    landing1        = Landingpage()   
    landing1.site           = site1
    site1.landingpages.append(landing1) 
    session.add(landing1)
    session.commit()    
    site1.default_landing = landing1.id    
    landing2        = Landingpage()
    landing2.site   = site2
    session.add(landing2)
    session.commit()
    site2.landingpages.append(landing2)
    session.add(landing2)
    site2.default_landing = landing2.id 
    session.commit()

    landing3        = Landingpage()
    landing3.site   = site3
    session.add(landing3)
    session.commit()  
    site3.landingpages.append(landing3)
    session.add(landing3)
    site3.default_landing = landing3.id 
    session.commit()    



