from unifispot.models import User
from unifispot.extensions import db
from flask.ext.security import current_user
from flask import current_app

from sqlalchemy import and_,or_
from unifispot.const import ROLE_SUPERADMIN,ACCOUNT_TYPE_FREE,ACCOUNT_TYPE_GOLD,ACCOUNT_TYPE_GOLD_PREM,ACCOUNT_TYPE_SILVER
from unifispot.base.utils.helper import dict_normalise_values
import datetime


class Superadmin(User):
    ''' Class to represent admin, each admin will be associated with a user of type admin

    '''
    id              = db.Column(db.Integer,db.ForeignKey('user.id'), primary_key=True)
    __mapper_args__ = {'polymorphic_identity': 'superadmin'}


    def check_admin(self):
        return False


    def check_superadmin(self):
        return True

    def get_user_type(self):  
        return ROLE_SUPERADMIN


    def get_admin_id(self):
        return NotImplemented

    def check_client(self):
        return False

class Account(db.Model):
    ''' Class to represent accounts. Each account can have multiple clients and admins


    '''
    id              = db.Column(db.Integer, primary_key=True)    
    name            = db.Column(db.String(60))
    unifi_server    = db.Column(db.String(255),index=True,default="localhost")    
    unifi_server_ip = db.Column(db.String(255),index=True,default="127.0.0.1")    
    unifi_user      = db.Column(db.String(255),index=True,default="ubnt")    
    unifi_pass      = db.Column(db.String(255),index=True,default="ubnt")    
    sites_allowed   = db.Column(db.Integer, default=0)     
    account_type    = db.Column(db.Integer,index=True,default=ACCOUNT_TYPE_FREE)
    expiresat       = db.Column(db.DateTime,index=True) 
    en_api_export   = db.Column(db.Integer, default=0,index=True) 
    en_reporting    = db.Column(db.Integer, default=0,index=True) 
    en_analytics    = db.Column(db.Integer, default=0,index=True) 
    en_advertisement= db.Column(db.Integer, default=0,index=True) 
    en_footer_change= db.Column(db.Integer, default=0,index=True) 
    en_fbauth_change= db.Column(db.Integer, default=0,index=True) 
    logins_allowed  = db.Column(db.Integer, default=100,index=True)   


    admins          = db.relationship('Admin', backref='account',lazy='dynamic') 
    clients         = db.relationship('Client', backref='account',lazy='dynamic') 
    sites           = db.relationship('Wifisite', backref='account',lazy='dynamic') 

    def populate_settings(self,form):
        self.unifi_server           = form.unifi_server.data
        self.unifi_server_ip        = form.unifi_server_ip.data
        self.unifi_user             = form.unifi_user.data
        self.unifi_pass             = form.unifi_pass.data 


    def get_settings(self):
        return dict_normalise_values({ 'unifi_server':self.unifi_server,'unifi_user':self.unifi_user, 'id':self.id, \
                    'unifi_pass':self.unifi_pass,'unifi_server_ip':self.unifi_server_ip}  )

    def populate_from_form(self,form):
        expiresat = datetime.datetime.strptime(form.expiresat.data , "%m/%d/%Y").date()
        self.unifi_server           = form.unifi_server.data
        self.unifi_server_ip        = form.unifi_server_ip.data
        self.unifi_user             = form.unifi_user.data
        self.unifi_pass             = form.unifi_pass.data        
        self.name                   = form.name.data        
        self.sites_allowed          = form.sites_allowed.data        
        self.account_type           = form.account_type.data        
        self.expiresat              = expiresat
        self.en_api_export          = form.en_api_export.data
        self.en_reporting           = form.en_reporting.data
        self.en_analytics           = form.en_analytics.data
        self.en_advertisement       = form.en_advertisement.data
        self.en_footer_change       = form.en_footer_change.data
        self.en_fbauth_change       = form.en_fbauth_change.data
        self.logins_allowed         = form.logins_allowed.data


    def to_dict(self):
        expiresat = self.expiresat.strftime("%m/%d/%Y") if self.expiresat else ''
        return dict_normalise_values({ 'unifi_server':self.unifi_server,'unifi_user':self.unifi_user, 'id':self.id, \
                    'unifi_pass':self.unifi_pass,'name':self.name,'sites_allowed':self.sites_allowed,'account_type':self.account_type,\
                    'expiresat':expiresat,'en_api_export':self.en_api_export,'en_reporting':self.en_reporting,\
                    'en_analytics':self.en_analytics,'en_advertisement':self.en_advertisement,'en_footer_change':self.en_footer_change,\
                    'en_fbauth_change':self.en_fbauth_change,'logins_allowed':self.logins_allowed
                    }  )


    #Search option with paging and sorting, uses LIKE on INDEXED fields 
    #and return num of total results  as well as number of rows controlled by paging
    def search_query(self,term,offset=0,limit=10,sort=None,modal_filters=None):
        main_query = Account.query
        if term:
            result_qry = main_query.filter(Account.name.like('%'+term+'%'))
        else:
            result_qry = main_query
        result_qry = result_qry.distinct( )
        total = result_qry.count()
        if sort['column'] == "0" :
            if sort['order'] == "desc":
                results_ord = result_qry.order_by(Account.name.desc())
            else:
                results_ord = result_qry.order_by(Account.name.asc())
        if sort['column'] == "1" :
            if sort['order'] == "desc":
                results_ord = result_qry.order_by(Account.sites_allowed.desc())
            else:
                results_ord = result_qry.order_by(Account.sites_allowed.asc())
        if sort['column'] == "2" :
            if sort['order'] == "desc":
                results_ord = result_qry.order_by(Account.account_type.desc())
            else:
                results_ord = result_qry.order_by(Account.account_type.asc())
        if sort['column'] == "3" :
            if sort['order'] == "desc":
                results_ord = result_qry.order_by(Account.expiresat.desc())
            else:
                results_ord = result_qry.order_by(Account.expiresat.asc())                
        else:
            results_ord = result_qry.order_by(Account.name.desc())  
        results = results_ord.offset(offset).limit(limit).all()
        return {'total':total,'results':results}

    def to_table_row(self):
        expiresat = self.expiresat.strftime("%m/%d/%Y") if self.expiresat else ''
        if self.account_type == ACCOUNT_TYPE_FREE:
            account_type = 'FREE'
        elif self.account_type == ACCOUNT_TYPE_SILVER:
            account_type = 'PERM'
        elif self.account_type == ACCOUNT_TYPE_GOLD:
            account_type = 'PERM'
        elif self.account_type == ACCOUNT_TYPE_GOLD_PREM:
            account_type = 'PERM'           
        return dict_normalise_values({'name':self.name,'sites_allowed':self.sites_allowed,'account_type':account_type,\
                    'expiresat':expiresat,'id':self.id}  )     