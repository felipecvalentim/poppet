from flask.ext.sqlalchemy import SQLAlchemy,SignallingSession, SessionBase
from flask.ext.security import RoleMixin,UserMixin
from flask.ext.security.utils import encrypt_password
from flask.ext.security import SQLAlchemyUserDatastore
from unifispot.extensions import db
from unifispot.base.utils.helper import dict_normalise_values
from unifispot.const import ROLE_ADMIN,ROLE_CLIENT


#Roles for flask-security
roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))
    def __repr__(self):
		return "<Role Name:%s Description:%s>"%(self.name,self.description)

#going to use joined table inheritance as given in http://docs.sqlalchemy.org/en/rel_1_0/orm/inheritance.html#joined-table-inheritance
class User(db.Model, UserMixin):
    id 	        = db.Column(db.Integer, primary_key=True)
    email       = db.Column(db.String(255), unique=True)
    password    = db.Column(db.String(255))
    roles		= db.relationship('Role', secondary=roles_users,backref=db.backref('users', lazy='dynamic'))
    displayname = db.Column(db.String(255))
    last_login_at = db.Column(db.String(255))
    current_login_at = db.Column(db.String(255))
    last_login_ip = db.Column(db.String(255))
    current_login_ip = db.Column(db.String(255))
    login_count = db.Column(db.Integer)
    confirmed_at = db.Column(db.String(255))
    active 		= db.Column(db.Boolean())
    type = db.Column(db.String(50))
    __mapper_args__ = {'polymorphic_identity': 'user',
            'polymorphic_on':type}
 		    

    def populate_from_form(self,form):
        self.email = form.email.data
        self.displayname = form.displayname.data
        if form.password.data:
            self.password = encrypt_password(form.password.data)

    def to_dict(self):
        return dict_normalise_values({'id':self.id,'email':self.email,'displayname':self.displayname})

    def __get_obj(self,obj,obj_id):
        if obj_id:
            obj_instance = obj.query.filter_by(id=obj_id).first()
        if obj_instance:
            return obj_instance


    #Search option with paging and sorting, uses LIKE on INDEXED fields 
    #and return num of total results  as well as number of rows controlled by paging
    def search_query(self,term,offset=0,limit=10,sort=None,modal_filters=None):
        main_query = User.query.filter_by()
        if term:
            result_qry = main_query.filter(or_( User.email.like('%'+term+'%'), User.displayname.like('%'+term+'%')))
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


user_datastore = SQLAlchemyUserDatastore(db,User,Role)



# Email throttling.
EMAIL_THROTTLE = 'unifispot:email_throttle:{md5}'  # Lock.

