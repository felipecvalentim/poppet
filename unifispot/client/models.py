from unifispot.models import User
from unifispot.extensions import db
from flask.ext.security import current_user
from flask import current_app
from unifispot.const import AUTH_TYPE_BYPASS,FACEBOOK_LIKE_OFF,FACEBOOK_POST_OFF
from sqlalchemy import and_,or_
from flask.ext.security.utils import encrypt_password




from unifispot.const import FORM_FIELD_ALL,CLIENT_REPORT_WEEKLY,FORM_FIELD_FIRSTNAME,FORM_FIELD_LASTNAME,FORM_FIELD_EMAIL,FORM_FIELD_PHONE,REDIRECT_ORIG_URL
from unifispot.base.utils.helper import dict_normalise_values
from unifispot.const import ROLE_ADMIN,ROLE_CLIENT,API_END_POINT_NONE,AUTH_TYPE_EMAIL,AUTH_TYPE_VOUCHER,AUTH_TYPE_SOCIAL,AUTH_TYPE_SMS,AUTH_TYPE_ALL


class Client(User):
    ''' Class to represent admin, each admin will be associated with a user of type admin

    '''
    id          = db.Column(db.Integer,db.ForeignKey('user.id'), primary_key=True)
    sites       = db.relationship('Wifisite', backref='client',lazy='dynamic')  
    __mapper_args__ = {'polymorphic_identity': 'client'}
    admin_id        = db.Column(db.Integer, db.ForeignKey('admin.id'))
    account_id      = db.Column(db.Integer, db.ForeignKey('account.id')) 

    #Search option with paging and sorting, uses LIKE on INDEXED fields 
    #and return num of total results  as well as number of rows controlled by paging
    def search_query(self,term,offset=0,limit=10,sort=None,modal_filters=None):
        if modal_filters:
            main_query = Client.query.filter_by(account_id=modal_filters['account_id'])
        else:
            main_query = Client.query
        if term:
            result_qry = main_query.filter(or_( Client.email.like('%'+term+'%'), Client.displayname.like('%'+term+'%')))
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
                'account_id':self.account_id
                }

    def to_dict(self):
        return {'displayname':self.displayname,
                'email':self.email,
                'id':self.id,
                'account_id':self.account_id
                }
    def populate_from_form(self,form):
        self.email = form.email.data
        self.displayname = form.displayname.data
        if form.password.data:
            self.password = encrypt_password(form.password.data)

    def check_admin(self):        
        return False

    def get_user_type(self):  
        return ROLE_CLIENT

    def check_client(self):
        return True

    def get_admin_id(self):
        return NotImplemented




        
class Wifisite(db.Model):
    ''' Class to represent wifi sites. Each client can have multiple sites


    '''
    id              = db.Column(db.Integer, primary_key=True)
    client_id       = db.Column(db.Integer, db.ForeignKey('client.id'))
    admin_id        = db.Column(db.Integer, db.ForeignKey('admin.id'))
    account_id      = db.Column(db.Integer, db.ForeignKey('account.id'))     
    name            = db.Column(db.String(255),index=True,default="defaultsite")  
    default_landing = db.Column(db.Integer)
    landingpages    = db.relationship('Landingpage', backref='site',lazy='dynamic')
    guests          = db.relationship('Guest', backref='site',lazy='dynamic')
    unifi_id        = db.Column(db.String(50),index=True,default="default")
    devices         = db.relationship('Device', backref='site',lazy='dynamic')    
    sessions        = db.relationship('Guestsession', backref='site',lazy='dynamic')    
    guesttracks     = db.relationship('Guesttrack', backref='site',lazy='dynamic')    
    sitefiles       = db.relationship('Sitefile', backref='site',lazy='dynamic')    
    facebookauths   = db.relationship('Facebookauth', backref='site',lazy='dynamic')    
    vouchers        = db.relationship('Voucher', backref='site',lazy='dynamic')    
    template        = db.Column(db.String(50),default='template1')    
    emailformfields = db.Column(db.Integer,default=(FORM_FIELD_LASTNAME+FORM_FIELD_FIRSTNAME))    
    auth_method     = db.Column(db.Integer,default=AUTH_TYPE_ALL)
    auth_fb_like    = db.Column(db.Integer,default=FACEBOOK_LIKE_OFF)
    auth_fb_post    = db.Column(db.Integer,default=FACEBOOK_POST_OFF)
    redirect_method = db.Column(db.Integer,default=REDIRECT_ORIG_URL)
    reports_type    = db.Column(db.Integer,default=CLIENT_REPORT_WEEKLY)
    reports_list    = db.Column(db.String(400))
    enable_redirect = db.Column(db.Boolean())
    redirect_url    = db.Column(db.String(200))
    fb_appid        = db.Column(db.String(200))
    fb_app_secret   = db.Column(db.String(200))
    fb_page         = db.Column(db.String(200),default='https://www.facebook.com/unifyhotspot')
    timezone        = db.Column(db.String(20),default='UTC')
    api_export      = db.Column(db.Integer,default=API_END_POINT_NONE)
    api_auth_field1 = db.Column(db.String(200))
    api_auth_field2 = db.Column(db.String(200))
    api_auth_field3 = db.Column(db.String(200))

    def populate_from_form(self,form):
        self.name               = form.name.data
        self.unifi_id           = form.unifi_id.data
        self.template           = form.template.data
        self.enablehtml	        = form.enablehtml.data
        self.auth_method	    = (form.auth_fb.data and AUTH_TYPE_SOCIAL) + (form.auth_phone.data and AUTH_TYPE_SMS) + (form.auth_voucher.data and AUTH_TYPE_VOUCHER)+ (form.auth_email.data and AUTH_TYPE_EMAIL)
        self.auth_fb_like	    = form.auth_fb_like.data
        self.auth_fb_post	    = form.auth_fb_post.data
        if self.account.en_advertisement:
            self.redirect_method	= form.redirect_method.data
            self.redirect_url       = form.redirect_url.data
        self.fb_page            = form.fb_page.data
        self.timezone           = form.timezone.data
        if self.account.en_fbauth_change:        
            self.fb_appid           = form.fb_appid.data
            self.fb_app_secret      = form.fb_app_secret.data
        if self.account.en_reporting:
            self.reports_type       = form.reports_type.data
            self.reports_list	    = form.reports_list.data
        self.emailformfields    = (form.get_lastname.data and FORM_FIELD_LASTNAME)  + (form.get_firstname.data and FORM_FIELD_FIRSTNAME)
        if self.account.en_api_export:
            self.api_export         = form.api_export.data
            self.api_auth_field1    = form.api_auth_field1.data
            self.api_auth_field2    = form.api_auth_field2.data
            self.api_auth_field3    = form.api_auth_field3.data

    def fb_login_en(self):
        return (self.auth_method & AUTH_TYPE_SOCIAL)

    def phone_login_en(self):
        return (self.auth_method & AUTH_TYPE_SMS)

    def voucher_login_en(self):
        return (self.auth_method & AUTH_TYPE_VOUCHER)

    def email_login_en(self):
        return (self.auth_method & AUTH_TYPE_EMAIL)        

    def to_dict(self):
        reports_type = None
        reports_list = None
        fb_appid = None
        fb_app_secret= None
        redirect_method = None
        redirect_url = None
        api_export = None
        api_auth_field1 = None
        api_auth_field2 = None
        api_auth_field3 = None
        if self.account.en_reporting:
            reports_type = self.reports_type
            reports_list = self.reports_list
        if self.account.en_fbauth_change:
            fb_appid = self.fb_appid
            fb_app_secret = self.fb_app_secret
        if self.account.en_advertisement:
            redirect_method = self.redirect_method
            redirect_url = self.redirect_url
        if self.account.en_api_export:
            api_export = self.api_export
            api_auth_field1 = self.api_auth_field1
            api_auth_field2 = self.api_auth_field2
            api_auth_field3 = self.api_auth_field3
        return dict_normalise_values({ 'name':self.name,'unifi_id':self.unifi_id, 'id':self.id, \
                'template':self.template,
                'get_lastname': (self.emailformfields &FORM_FIELD_LASTNAME),\
                'get_firstname': (self.emailformfields &FORM_FIELD_FIRSTNAME),\
                'auth_fb':(self.auth_method &AUTH_TYPE_SOCIAL),'auth_email':(self.auth_method &AUTH_TYPE_EMAIL),\
                'auth_phone':(self.auth_method &AUTH_TYPE_SMS),'auth_voucher':(self.auth_method &AUTH_TYPE_VOUCHER),\
                'default_landing':self.default_landing,'reports_type':reports_type, \
                'fb_page':self.fb_page,'auth_fb_like':self.auth_fb_like,'auth_fb_post':self.auth_fb_post,\
                'fb_appid':fb_appid,'fb_app_secret':fb_app_secret,
                'redirect_method':redirect_method,'redirect_url':redirect_url,'timezone':self.timezone,\
                'emailformfields':self.emailformfields,'reports_list':reports_list,'client_id':self.client.id,\
                'api_export':api_export,'api_auth_field1':api_auth_field1,'api_auth_field2':api_auth_field2,\
                'api_auth_field3':api_auth_field3})



    #Search option with paging and sorting, uses LIKE on INDEXED fields 
    #and return num of total results  as well as number of rows controlled by paging
    def search_query(self,term,offset=0,limit=10,sort=None,modal_filters=None):        
        main_query = Wifisite.query.filter_by()
        if term:
            result_qry = main_query
        else:
            result_qry = main_query
        result_qry = result_qry.distinct( )
        total = result_qry.count()
        if sort['column'] == "0" :
            if sort['order'] == "desc":
                results_ord = result_qry.order_by(Wifisite.name.desc())
            else:
                results_ord = result_qry.order_by(Wifisite.name.asc())
        else:
            results_ord = result_qry.order_by(Landingpage.id.asc()) 
        results = results_ord.offset(offset).limit(limit).all()
        return {'total':total,'results':results}       
 

class Landingpage(db.Model):
    ''' Class to represent landing page design

    '''
    id              = db.Column(db.Integer, primary_key=True)
    site_id         = db.Column(db.Integer, db.ForeignKey('wifisite.id'))
    logofile        = db.Column(db.String(200),default='/static/img/logo.png')
    bgfile          = db.Column(db.String(200),default='/static/img/bg.jpg')
    pagebgcolor     = db.Column(db.String(10),default='#ffffff')
    bgcolor         = db.Column(db.String(10),default='#ffffff')
    headerlink      = db.Column(db.String(200))
    basefont        = db.Column(db.Integer,default=2)
    topbgcolor      = db.Column(db.String(10),default='#ffffff')
    toptextcolor    = db.Column(db.String(10))
    topfont         = db.Column(db.Integer,default=2)
    toptextcont     = db.Column(db.String(2000),default='Please Sign In for WiFi')
    middlebgcolor   = db.Column(db.String(10),default='#ffffff')
    middletextcolor = db.Column(db.String(10))
    middlefont      = db.Column(db.Integer,default=2)
    bottombgcolor   = db.Column(db.String(10),default='#ffffff')
    bottomtextcolor = db.Column(db.String(10))
    bottomfont      = db.Column(db.Integer,default=2)
    bottomtextcont  = db.Column(db.String(2000))
    footerbgcolor   = db.Column(db.String(10),default='#ffffff')
    footertextcolor = db.Column(db.String(10))
    footerfont      = db.Column(db.Integer,default=2)
    footertextcont  = db.Column(db.String(2000))
    btnbgcolor      = db.Column(db.String(10))
    btntxtcolor     = db.Column(db.String(10))
    btnlinecolor    = db.Column(db.String(10),default='#000000')
    tosfile         = db.Column(db.String(200),default='/static/img/tos.pdf')
    copytextcont    = db.Column(db.String(2000))


    def populate_from_form(self,form):
        self.site_id        = form.site_id.data
        self.logofile       = form.logofile.data
        self.bgfile         = form.bgfile.data
        self.pagebgcolor    = form.pagebgcolor.data
        self.bgcolor        = form.bgcolor.data
        self.headerlink     = form.headerlink.data
        self.basefont       = form.basefont.data
        self.topbgcolor     = form.topbgcolor.data
        self.toptextcolor   = form.toptextcolor.data
        self.topfont        = form.topfont.data
        self.toptextcont    = form.toptextcont.data
        self.middlebgcolor  = form.middlebgcolor.data
        self.middletextcolor= form.middletextcolor.data
        self.middlefont     = form.middlefont.data
        self.bottombgcolor  = form.bottombgcolor.data
        self.bottomtextcolor= form.bottomtextcolor.data
        self.bottomfont     = form.bottomfont.data
        self.footerbgcolor  = form.footerbgcolor.data
        self.footertextcolor= form.footertextcolor.data
        self.footerfont     = form.footerfont.data
        self.footertextcont = form.footertextcont.data
        self.btnbgcolor     = form.btnbgcolor.data
        self.btntxtcolor    = form.btntxtcolor.data
        self.btnlinecolor   = form.btnlinecolor.data
        self.tosfile        = form.tosfile.data
        self.copytextcont   = form.copytextcont   .data


    #Search option with paging and sorting, uses LIKE on INDEXED fields 
    #and return num of total results  as well as number of rows controlled by paging
    def search_query(self,term,offset=0,limit=10,sort=None,modal_filters=None):        
        main_query = Landingpage.query.filter(and_(Landingpage.site_id==modal_filters['siteid'],Landingpage.demo==False))
        if term:
            result_qry = main_query
        else:
            result_qry = main_query
        result_qry = result_qry.distinct( )
        total = result_qry.count()
        if sort['column'] == "0" :
            if sort['order'] == "desc":
                results_ord = result_qry.order_by(Landingpage.name.desc())
            else:
                results_ord = result_qry.order_by(Landingpage.name.asc())
        else:
            results_ord = result_qry.order_by(Landingpage.id.asc()) 
        results = results_ord.offset(offset).limit(limit).all()
        return {'total':total,'results':results}

    def to_table_row(self):
        return {'name':self.name,
            'site_id':self.site_id,
            'id':self.id
        }
    def to_dict(self):
        return dict_normalise_values({
            'id':self.id,
            'site_id':self.site_id,
            'logofile':self.logofile,
            'bgfile':self.bgfile,
            'pagebgcolor':self.pagebgcolor,
            'bgcolor':self.bgcolor ,
            'headerlink':self.headerlink,
            'basefont':self.basefont,
            'topbgcolor':self.topbgcolor,
            'toptextcolor':self.toptextcolor ,
            'topfont':self.topfont,
            'toptextcont':self.toptextcont ,
            'middlebgcolor':self.middlebgcolor ,
            'middletextcolor':self.middletextcolor,
            'middlefont':self.middlefont,
            'bottombgcolor':self.bottombgcolor ,
            'bottomtextcolor':self.bottomtextcolor,
            'bottomfont':self.bottomfont,
            'footerbgcolor':self.footerbgcolor,
            'footertextcolor':self.footertextcolor ,
            'footerfont':self.footerfont,
            'footertextcont':self.footertextcont ,
            'btnbgcolor':self.btnbgcolor,
            'btntxtcolor':self.btntxtcolor  ,
            'btnlinecolor':self.btnlinecolor,
            'tosfile':self.tosfile,
            'copytextcont':self.copytextcont  
        })



#entry to store the details of uploaded files
class Sitefile(db.Model):
    ''' Class to represent Files, each entry will point to a file stored in the HD

    '''
    id              = db.Column(db.Integer, primary_key=True)   
    site_id         = db.Column(db.Integer, db.ForeignKey('wifisite.id'))
    file_location   = db.Column(db.String(255))
    file_type       =  db.Column(db.Integer)
    file_thumb_location = db.Column(db.String(255))
    file_label      = db.Column(db.String(255))

    def to_dict(self):
        return { 'file_location':self.file_location,
                    'id':self.id,'file_type':self.file_type,
                    'file_thumb_location':self.file_thumb_location,
                    'file_label':self.file_label}

    def populate_from_form(self,form):
        self.file_label     = form.file_label.data

    def update_ownership(self,request):
        siteid =  request.view_args.get('siteid')
        self.site_id = siteid

    def get_file_path(self,fileid):
        if fileid == 0:
            return '/static/img/default_file.png'
        file_path = Sitefile.query.filter_by(id=fileid).first()
        return file_path


#Store vouchers
class  Voucher(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    batchid         = db.Column(db.String(40),index=True)
    voucher         = db.Column(db.String(20),index=True)
    notes           = db.Column(db.String(50),index=True)
    duration_t      = db.Column(db.BigInteger())
    used            = db.Column(db.Boolean(),default=False,index=True)
    site_id         = db.Column(db.Integer, db.ForeignKey('wifisite.id'))
    duration        = db.Column(db.String(20),index=True)
    used_at         = db.Column(db.DateTime,index=True)   #used time in UTC,filled once voucher is used
    device_id       = db.Column(db.Integer, db.ForeignKey('device.id'))

    def populate_from_form(self,form):
        self.notes = form.notes.data
        #set duration accordingly
        if form.duration_t.data == 1:
            self.duration    = form.duration.data + ' Hours'
            self.duration_t  = int(form.duration.data) * 60 * 60
        elif form.duration_t.data == 2:
            self.duration    = form.duration.data + ' Days'
            self.duration_t  = int(form.duration.data) * 60 * 60 * 24
        elif form.duration_t.data == 3:
            self.duration    = form.duration.data + ' Months'   
            self.duration_t  = int(form.duration.data) * 60 * 60 * 24 * 30  


    def to_dict(self):

        return {'site':self.site.name,'duration':self.duration,
                'status':'<span class="label label-danger">Used</span>' if self.used else '<span class="label label-success">Initializing</span>',
                'voucher':self.voucher,'note':self.notes,
                'id':self.id
                }                 

        return dict_server

    #Search option with paging and sorting, uses LIKE on INDEXED fields 
    #and return num of total results  as well as number of rows controlled by paging
    def search_query(self,term,offset=0,limit=10,sort=None,modal_filters=None):
        main_query = Voucher.query.filter_by(site_id=modal_filters['siteid'])
        if term:
            result_qry = main_query.outerjoin(Voucher.site).filter(or_( Wifisite.name.like('%'+term+'%'), Voucher.voucher.like('%'+term+'%'), Voucher.notes.like('%'+term+'%')))
        else:
            result_qry = main_query
        result_qry = result_qry.distinct( )
        total = result_qry.count()
        if sort['column'] == "0" :
            if sort['order'] == "desc":
                results_ord = result_qry.order_by(Wifisite.name.desc())
            else:
                results_ord = result_qry.order_by(Wifisite.name.asc())
        elif sort['column'] == "1" :
            if sort['order'] == "desc":
                results_ord = result_qry.order_by(Voucher.voucher.desc())
            else:
                results_ord = result_qry.order_by(Voucher.voucher.desc())
        elif sort['column'] == "2" :
            if sort['order'] == "desc":
                results_ord = result_qry.order_by(Voucher.duration.desc())
            else:
                results_ord = result_qry.order_by(Voucher.duration.desc())          
        elif sort['column'] == "3" :
            if sort['order'] == "desc":
                results_ord = result_qry.order_by(Voucher.used.desc())
            else:
                results_ord = result_qry.order_by(Voucher.used.desc())        
        elif sort['column'] == "4" :
            if sort['order'] == "desc":
                results_ord = result_qry.order_by(Voucher.notes.desc())
            else:
                results_ord = result_qry.order_by(Voucher.notes.desc())    
        else:
            results_ord = result_qry.order_by(Voucher.id.asc())  
        results = results_ord.offset(offset).limit(limit).all()
        return {'total':total,'results':results}

    def to_table_row(self):

        return {'site':self.site.name,'duration':self.duration,
                'status':'<span class="label label-danger">Used</span>' if self.used else '<span class="label label-primary">Available</span>',
                'voucher':self.voucher,'note':self.notes,
                'id':self.id
                }