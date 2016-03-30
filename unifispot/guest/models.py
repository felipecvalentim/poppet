from unifispot.extensions import db
import datetime
import uuid
from unifispot.const import *
from sqlalchemy_utils import ArrowType
from sqlalchemy import and_,or_
import arrow

class Guest(db.Model):
    ''' Class to represent guest profile, it will be filled fully/partially depending upon site configuration

    '''
    id          = db.Column(db.Integer, primary_key=True)
    site_id     = db.Column(db.Integer, db.ForeignKey('wifisite.id')) 
    firstname   = db.Column(db.String(60))
    lastname    = db.Column(db.String(60))
    age         = db.Column(db.Integer,index=True)
    gender      = db.Column(db.Integer,index=True)
    state       = db.Column(db.Integer,index=True)
    email       = db.Column(db.String(60))
    phonenumber = db.Column(db.String(15))
    devices     = db.relationship('Device', backref='guest',lazy='dynamic')
    fb_profile  = db.Column(db.Integer, db.ForeignKey('facebookauth.id'))
    fb_liked    = db.Column(db.Integer)
    fb_posted   = db.Column(db.Integer)
    created_at  = db.Column(db.DateTime,default=datetime.datetime.utcnow,index=True)
    apisync     = db.Column(db.Integer,index=False)  #Flag to be set after syncing to API
    synchedat   = db.Column(db.DateTime,index=True) #synched time in UTC
    demo        = db.Column(db.Boolean(),default=0,index=True)



    def populate_from_email_form(self,form,form_fields):
        if hasattr(form,'email'):
            self.email = form.email.data        
        if hasattr(form,'firstname'):
            self.firstname = form.firstname.data
        if hasattr(form,'lastname'):
            self.lastname = form.lastname.data
        if hasattr(form,'phonenumber'):
            self.phonenumber = form.phonenumber.data


    def search_query(self,term,offset=0,limit=10,sort=None,modal_filters=None):
        main_query = Guest.query.filter(and_(Guest.site_id==modal_filters['siteid'],Guest.demo ==0))
        if term:
            result_qry = main_query
        else:
            result_qry = main_query
        result_qry = result_qry.distinct( )
        total = result_qry.count()
        if sort['column'] == "0" :
            if sort['order'] == "desc":
                results_ord = result_qry.order_by(Guest.firstname.desc())
            else:
                results_ord = result_qry.order_by(Guest.firstname.asc())
        elif sort['column'] == "1" :
            if sort['order'] == "desc":
                results_ord = result_qry.order_by(Guest.lastname.desc())
            else:
                results_ord = result_qry.order_by(Guest.lastname.asc())       
        elif sort['column'] == "2" :
            if sort['order'] == "desc":
                results_ord = result_qry.order_by(Guest.age.desc())
            else:
                results_ord = result_qry.order_by(Guest.age.asc())  
        elif sort['column'] == "3" :
            if sort['order'] == "desc":
                results_ord = result_qry.order_by(Guest.gender.desc())
            else:
                results_ord = result_qry.order_by(Guest.gender.asc())  
        elif sort['column'] == "4" :
            if sort['order'] == "desc":
                results_ord = result_qry.order_by(Guest.phonenumber.desc())
            else:
                results_ord = result_qry.order_by(Guest.phonenumber.asc())  
        elif sort['column'] == "5" :
            if sort['order'] == "desc":
                results_ord = result_qry.order_by(Guest.email.desc())
            else:
                results_ord = result_qry.order_by(Guest.email.asc())                                  
        else:
            results_ord = result_qry.order_by(Guest.firstname.asc())  
        results = results_ord.offset(offset).limit(limit).all()
        print {'total':total,'results':results}
        return {'total':total,'results':results}


    def to_table_row(self):

        return {'firstname':self.firstname,'age':self.age,'email':self.email,
                'lastname':self.lastname,'phonenumber':self.phonenumber,
                'id':self.id,'gender':self.gender
                }

class Device(db.Model):
    ''' Class to represent guest's device, each guest can have multiple devices attached to his account

    '''
    id          = db.Column(db.Integer, primary_key=True)
    mac         = db.Column(db.String(30),index=True)
    hostname    = db.Column(db.String(60),index=True)
    state       = db.Column(db.Integer)
    created_at  = db.Column(db.DateTime,default=datetime.datetime.utcnow,index=True)
    guest_id    = db.Column(db.Integer, db.ForeignKey('guest.id'))
    site_id     = db.Column(db.Integer, db.ForeignKey('wifisite.id'))
    sessions    = db.relationship('Guestsession', backref='device',lazy='dynamic')
    smsdatas    = db.relationship('Smsdata', backref='device',lazy='dynamic')
    expires_at  = db.Column(db.DateTime)          #Expiry time for last used voucher  , valid only if state is Device_voucher_auth
    demo        = db.Column(db.Integer,default=0,index=True)

class Guestsession(db.Model):
    ''' Class to represent guest session. Each session is associated to a Guest and will have a state associated with it.

    '''
    id          = db.Column(db.Integer, primary_key=True)
    site_id     = db.Column(db.Integer, db.ForeignKey('wifisite.id'))
    device_id   = db.Column(db.Integer, db.ForeignKey('device.id'))
    starttime   = db.Column(db.DateTime,default=datetime.datetime.utcnow,index=True)
    lastseen    = db.Column(db.DateTime,index=True,default=datetime.datetime.utcnow)
    stoptime    = db.Column(db.DateTime,index=True)   #Time at which session is stopped, to be filled by session updator
    expiry      = db.Column(db.DateTime,index=True,default=datetime.datetime.utcnow)   #predicted expiry time,default to 60 minutes
    temp_login  = db.Column(db.Integer,default=0)
    duration    = db.Column(db.Integer,default=60)
    ban_ends    = db.Column(db.DateTime,index=True)
    data_used   = db.Column(db.String(20))            #Data used up in this session
    state       = db.Column(db.Integer)
    mac         = db.Column(db.String(30),index=True)
    d_updated   = db.Column(db.String(20))            #data updated last
    duration    = db.Column(db.Integer)               #Duration in seconds the session lasted, updated by session updator   
    guesttracks = db.relationship('Guesttrack', backref='guestsession',lazy='dynamic')
    demo        = db.Column(db.Integer,default=0,index=True)

class Guesttrack(db.Model):
    ''' Class to track connection attempts, this is also used to track login process

    '''
    id          = db.Column(db.Integer, primary_key=True)
    track_id    = db.Column(db.String(40),index=True,unique=True)
    site_id     = db.Column(db.Integer, db.ForeignKey('wifisite.id'))
    session_id  = db.Column(db.Integer, db.ForeignKey('guestsession.id'))
    ap_mac      = db.Column(db.String(20),index=True)
    device_mac  = db.Column(db.String(20),index=True)
    timestamp   = db.Column(db.DateTime,default=datetime.datetime.utcnow,index=True)
    state       = db.Column(db.Integer,index=True)
    fb_liked    = db.Column(db.Integer,index=True,default=0)
    fb_posted   = db.Column(db.Integer,index=True,default=0)
    orig_url    = db.Column(db.String(200))
    demo        = db.Column(db.Integer,default=0,index=True)

class Facebookauth(db.Model):
    ''' Class to represent guest's Facebook connection, this is needed as one common APP is used for tracking guests in different sites.

    '''
    id          = db.Column(db.Integer, primary_key=True)
    profile_id  = db.Column(db.String(30), nullable=False,index=True)
    site_id     = db.Column(db.Integer, db.ForeignKey('wifisite.id'))    
    token       = db.Column(db.String(100), nullable=False)
    state       = db.Column(db.Integer)
    guests      = db.relationship('Guest', backref='facebookauth',lazy='dynamic')
    
class Smsdata(db.Model):
    ''' Class to represent Device's SMS data

    '''
    id          = db.Column(db.Integer, primary_key=True)
    site_id     = db.Column(db.Integer, db.ForeignKey('wifisite.id'))    
    device_id    = db.Column(db.Integer, db.ForeignKey('device.id'))    
    phonenumber = db.Column(db.String(20),index=True)    
    authcode    = db.Column(db.String(20),index=True)    
    timestamp   = db.Column(db.DateTime,default=datetime.datetime.utcnow)
    status      = db.Column(db.Integer, index=True,default=SMS_DATA_NEW)
    send_try    = db.Column(db.Integer, index=True,default=0)