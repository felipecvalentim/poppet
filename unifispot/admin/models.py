from unifispot.models import User
from unifispot.extensions import db
from flask.ext.security import current_user
from flask import current_app

from sqlalchemy import and_,or_
from unifispot.const import ROLE_ADMIN,ROLE_CLIENT
from flask.ext.security.utils import encrypt_password

class Admin(User):
    ''' Class to represent admin, each admin will be associated with a user of type admin

    '''
    id              = db.Column(db.Integer,db.ForeignKey('user.id'), primary_key=True)
    sites           = db.relationship('Wifisite', backref='admin',lazy='dynamic')  
    account_id      = db.Column(db.Integer, db.ForeignKey('account.id')) 
    __mapper_args__ = {'polymorphic_identity': 'admin'}



    def check_admin(self):
        return True

    def get_user_type(self):  
        return ROLE_ADMIN


    def get_admin_id(self):
        return NotImplemented

    def check_client(self):
        return False

    #Search option with paging and sorting, uses LIKE on INDEXED fields 
    #and return num of total results  as well as number of rows controlled by paging
    def search_query(self,term,offset=0,limit=10,sort=None,modal_filters=None):
        if modal_filters:
            main_query = Admin.query.filter_by(account_id=modal_filters['account_id'])
        else:
            main_query = Admin.query

        if term:
            result_qry = main_query.outerjoin(Admin.account).filter(or_( Admin.email.like('%'+term+'%'),\
             Admin.displayname.like('%'+term+'%')))
        else:
            result_qry = main_query
        result_qry = result_qry.distinct( )
        total = result_qry.count()
        if sort['column'] == "0" :
            if sort['order'] == "desc":
                results_ord = result_qry.order_by(User.email.desc())
            else:
                results_ord = result_qry.order_by(User.email.asc())
        else:
            results_ord = result_qry.order_by(User.id.asc())  
        results = results_ord.offset(offset).limit(limit).all()
        return {'total':total,'results':results}

    def to_table_row(self):
        return {'displayname':self.displayname,
                'email':self.email,
                'id':self.id,
                'account':self.account.name
                }
    def populate_from_form(self,form):
        self.email = form.email.data
        self.displayname = form.displayname.data
        if form.password.data:
            self.password = encrypt_password(form.password.data)

    def to_dict(self):
        return {'displayname':self.displayname,
                'email':self.email,
                'id':self.id,
                'account_id':self.account_id
                }