from flask import jsonify,abort,request,current_app
from flask.ext.security import current_user
from sqlalchemy.exc import IntegrityError

from .models import Wifisite,Landingpage,Sitefile,Client,Voucher
from .forms import WifiSiteForm,LandingPageForm,SiteFileForm,VoucherForm

from unifispot.base.api import UnifispotAPI
from unifispot.base.file import FileAPI
from unifispot.base.datatable import DataTablesServer
from unifispot.extensions import db
from unifispot.base.utils.forms import print_errors,get_errors
from unifispot.models import User,user_datastore,Role
from unifispot.guest.models import Guest,Guestsession,Device,Guesttrack

from functools import wraps
from urlparse import urlparse
from hashids import Hashids
from random import randint
import uuid

              
class WifisiteAPI(UnifispotAPI):

    ''' API class to deal with wifisite entries
    
    '''

    def __init__(self):
        super(self.__class__, self).__init__()
        self.columns = ['name','unifi_id']
        self.entity_name = 'Site Details'
        
    def get_modal_obj(self):
        return Wifisite()

    def get_form_obj(self):
        return WifiSiteForm()
      
    def datatable_obj(self,request,columns,index_column,db,modal_obj):
        return DataTablesServer(request,columns,index_column,db,modal_obj)
        
    def validate_url(f):
        #Validate that client is trying to view only the sites owned by him
        @wraps(f)
        def decorated_function(*args, **kwargs):
            id =  request.view_args.get('id')
            #perform additional permission checks
            if not  current_app.config['LOGIN_DISABLED']:                
                if id:
                    wifisite = Wifisite.query.filter_by(id=id).first()
                    if not wifisite:
                        current_app.logger.debug("Unknown Site ID: %s "%(request.url))
                        return jsonify({'status': 0,'msg':'Unknown Site ID'})
                    #client users have access only to sites owned by them
                    if current_user.type == 'client'  and  wifisite.client_id != current_user.id:
                        current_app.logger.debug("Client trying to access unauthorized URL %s "%(request.url))
                        return jsonify({'status': 0,'msg':'Not Authorized'})     
                    #admin users have access only to sites in their account  
                    if current_user.type == 'admin'  and  wifisite.account_id != current_user.account_id:
                        current_app.logger.debug("Admin trying to access unauthorized URL %s "%(request.url))
                        return jsonify({'status': 0,'msg':'Not Authorized'})  
            return f(*args, **kwargs)
        return decorated_function
    #
    @validate_url
    def get(self,id):   
        if id is None:
            if current_user.type == 'admin':
                 # return a list of all elements    
                items = self.get_modal_obj().query.filter_by(account_id=current_user.account_id).all()
            else:
                items = self.get_modal_obj().query.filter_by(client_id=current_user.id).all()
            results = []
            for item in items:
                results.append(item.to_dict())
            num_sites = len(results)
            sites_available = current_user.account.sites_allowed - num_sites
            return jsonify({'status':1,'data':results,'sites_available':sites_available})                    
        return super(WifisiteAPI, self).get(id)

    @validate_url
    def post(self,id): 
        if id is None:
            if not current_user.type == 'admin':
                current_app.logger.debug("Client trying to access unauthorized URL %s "%(request.url))
                return jsonify({'status': 0,'msg':'Not Authorized'})    
            num_sites = Wifisite.query.filter_by(account_id=current_user.account_id).count()        
            if  current_user.account.sites_allowed <= num_sites :
                return jsonify({'status': 0,'msg':'Not enough credit to create a site'})
             # create a new element
            form1 = self.get_form_obj()
            form1.populate()
            if  form1.validate_on_submit():  
                try:      
                    newitem = self.get_modal_obj()
                    db.session.add(newitem)
                    client = Client.query.filter_by(id=form1.client_id.data).first()
                    newitem.client = client
                    newitem.admin = current_user
                    newitem.account_id = current_user.account_id                
                    newitem.populate_from_form(form1)
                    newlanding = Landingpage()                         
                    db.session.add(newlanding)                   
                    db.session.commit()
                    newlanding.site = newitem
                    newitem.default_landing = newlanding.id                     
                    db.session.commit()
                except IntegrityError:
                    return jsonify({'status': 0,'msg':'Value already exists in the database for :%s'%self.entity_name})
                else:
                    return jsonify({'status': 1,'id':newitem.id,'msg':'Added New Entry for:%s into Database'%self.entity_name})
            else:
                print_errors(form1)
                return jsonify({'status':0,'msg': get_errors(form1)})
        else:
        # update a single item
            singleitem = self.get_modal_obj().query.filter_by(id=id).first()
            if singleitem:
                form1 = self.get_form_obj()
                form1.populate()
                if form1.validate_on_submit():                                
                    singleitem.populate_from_form(form1)
                    try:
                        db.session.commit()
                    except IntegrityError:
                        return jsonify({'status': 0,'msg':'Value already exists in the database for:%s'%self.entity_name})
                    else:
                        return jsonify({'status': 1,'msg':'Updated :%s'%self.entity_name})
                else:
                    return jsonify({'status':0,'msg': get_errors(form1)})
            return jsonify({'status':0,'err': 'Some Error Occured while processing:%s'%self.entity_name})  

    @validate_url
    def delete(self,id):
        if not current_user.type == 'admin':
            current_app.logger.debug("Client trying to access unauthorized URL %s "%(request.url))
            return jsonify({'status': 0,'msg':'Not Authorized'})          
        #delete all connected items
        #Landing pages,Guest,Device,Guestsession,Guesttrack,Sitefile
        try:
            [db.session.delete(item) for item in Landingpage.query.filter_by(site_id=id).all()]
            [db.session.delete(item) for item in Guest.query.filter_by(site_id=id).all()]
            [db.session.delete(item) for item in Device.query.filter_by(site_id=id).all()]
            [db.session.delete(item) for item in Guestsession.query.filter_by(site_id=id).all()]
            [db.session.delete(item) for item in Guesttrack.query.filter_by(site_id=id).all()]
            [db.session.delete(item) for item in Sitefile.query.filter_by(site_id=id).all()]
            [db.session.delete(item) for item in Voucher.query.filter_by(site_id=id).all()]
            db.session.commit()
        except:
            current_app.logger.exception('Exception while trying to delete Wifisite ID:%s'%id)
            return jsonify({'status':0,'err': 'Some Error Occured while processing:%s'%self.entity_name})
        return super(WifisiteAPI, self).delete(id)
                
              
class LandingPageAPI(UnifispotAPI):

    ''' API class to deal with LandingPage entries
    
    '''
    def __init__(self):
        super(self.__class__, self).__init__()
        self.columns = ['name']
        self.entity_name = 'Landing Page'
        
    def get_template_name(self):
        return ''

    def get_modal_obj(self):
        return Landingpage()

    def get_form_obj(self):
        return LandingPageForm()

    def api_path(self):
        return '/clients/site/<int:siteid>/landing/api/'
        
    def datatable_obj(self,request,columns,index_column,db,modal_obj,modal_filter):

        return None
        
    def validate_url(f):
        #Validate that client is trying to view only the sites owned by him
        @wraps(f)
        def decorated_function(*args, **kwargs):
            id =  request.view_args.get('id')
            siteid =  request.view_args.get('siteid')  
            wifisite = Wifisite.query.filter_by(id=siteid).first()
            if not wifisite:
                current_app.logger.debug("Client  is trying to unknown site ID:%s "%(request.url))
                abort(404)   
            #admin user can have full access
            #perform additional permission checks
            if not  current_app.config['LOGIN_DISABLED']:
                if not current_user.check_admin():
                    return jsonify({'status': 0,'msg':'Not Authorized'}) 
            if id:
                #check if site ID is owned by the client
                #check if landingpage ID is belongs to the site
                landpage = Landingpage.query.filter_by(id=id).first()
                if not landpage:
                    current_app.logger.debug("Trying to aceess invalid landingpage ID:%s "%(request.url))
                    abort(404) 
                if landpage.site_id != wifisite.id:
                    current_app.logger.debug("Trying to aceess invalid landingpage ID:%s "%(request.url))
                    abort(401)                      
            return f(*args, **kwargs)
        return decorated_function
    #
    @validate_url   
    def get(self,siteid,id):   
        if id is None:
            # return a list of all elements    
            items = self.get_modal_obj().query.filter_by(site_id=siteid).all()
            results = []
            for item in items:
                results.append(item.to_dict())
            return jsonify({'status':1,'data':results})     
        return super(LandingPageAPI, self).get(id)
    @validate_url
    def post(self,siteid,id):             
        if id is None:
        # create a new element
            form1 = self.get_form_obj()
            form1.populate(siteid)
            if  form1.validate_on_submit():        
                newitem = self.get_modal_obj()
                if form1.site_id.data != siteid:
                    current_app.logger.error("Wrong site_id is specified in form value!! Someone is trying to mess!! URL:%s"%request.url)
                    return jsonify({'status': 0,'msg':'Wrong Site ID specified!!'})

                newitem.populate_from_form(form1)
                try:
                    db.session.add(newitem)
                    db.session.commit()
                except IntegrityError:
                    return jsonify({'status': 0,'msg':'Value already exists in the database for :%s'%self.entity_name})
                else:
                    return jsonify({'status': 1,'id':newitem.id,'msg':'Added New Entry for:%s into Database'%self.entity_name})
            else:
                print_errors(form1)
                return jsonify({'status':0,'msg': get_errors(form1)})

        else:
        # update a single item
            singleitem = self.get_modal_obj().query.filter_by(id=id).first()
            if singleitem:
                form1 = self.get_form_obj()
                form1.populate(siteid)
                if form1.validate_on_submit():
                    if form1.site_id.data != siteid:
                        current_app.logger.error("Wrong site_id is specified in form value!! Someone is trying to mess!! URL:%s"%request.url)
                        return jsonify({'status': 0,'msg':'Wrong Site ID specified!!'})                    
                    singleitem.populate_from_form(form1)
                    try:
                        db.session.commit()
                    except IntegrityError:
                        return jsonify({'status': 0,'msg':'Value already exists in the database for:%s'%self.entity_name})
                    else:
                        return jsonify({'status': 1,'msg':'Updated :%s'%self.entity_name,'id':singleitem.id})
                else:
                    return jsonify({'status':0,'msg': get_errors(form1)})
            return jsonify({'status':0,'err': 'Some Error Occured while processing:%s'%self.entity_name})
    @validate_url
    def delete(self,siteid,id):     
        return super(LandingPageAPI, self).delete(id)
                                                                          
class SiteFileAPI(FileAPI):

    ''' API class to deal with client site files
    
    '''

    def __init__(self):
        super(self.__class__, self).__init__()   
        self.upload_folder = current_app.config['SITE_FILE_UPLOAD'] 
        self.base_folder = current_app.config['BASE_FOLDER'] 

    def get_modal_obj(self):
        return Sitefile()

    def get_form_obj(self):
        return SiteFileForm()

    def validate_url(f):
        #Validate that client is trying to view only the sites owned by him
        @wraps(f)
        def decorated_function(*args, **kwargs):
            id =  request.view_args.get('id')
            siteid =  request.view_args.get('siteid')            
            #perform additional permission checks
            if not  current_app.config['LOGIN_DISABLED']:
                if not current_user.check_admin():
                    return jsonify({'status': 0,'msg':'Not Authorized'}) 
            wifisite = Wifisite.query.filter_by(id=siteid).first()
            if not wifisite:
                current_app.logger.debug("Trying to acess unknown site ID:%s "%(request.url))
                abort(404)     
            #check if File ID is belongs to the site
            if id is not None:
                filetocheck = Sitefile.query.filter_by(id=id).first()
                if not filetocheck:
                    current_app.logger.debug("Trying to access unknown File:%s "%(request.url))
                    abort(404) 
                if filetocheck.site_id != wifisite.id:
                    current_app.logger.debug("Trying to access file which is not connected to the site ID specified URL:%s "%(request.url))
                    abort(401)                      
            return f(*args, **kwargs)
        return decorated_function
    #
    @validate_url
    def get(self,siteid,id):
        if id is None:
            files_to_show = Sitefile.query.filter_by(site_id=siteid).all() 
            files = []
            if not  files_to_show:
                return jsonify({'status':0,'msg':'No Files found for this site.'})
            for file_to_show in files_to_show:        
                files.append(file_to_show.to_dict())
            return jsonify({'status':1,'data':files,'msg':'Successfully returning Files'})
        return super(SiteFileAPI, self).get(id)

    @validate_url
    def post(self,siteid,id):        
        return super(SiteFileAPI, self).post(id)

    @validate_url
    def delete(self,siteid,id):        
        return super(SiteFileAPI, self).delete(id)

class GuestdataAPI(UnifispotAPI):


    ''' API class to deal with LandingPage entries
    
    '''
    def __init__(self):
        super(self.__class__, self).__init__()
        self.columns = ['firstname','lastname','age','gender','phonenumber','email']
        self.entity_name = 'Guest Data'
        
    def get_template_name(self):
        return ''

    def get_modal_obj(self):
        return Guest()

    def get_form_obj(self):
        return None

    def api_path(self):
        return '/clients/<int:clientid>/site/<int:siteid>/landing/api/'
        
    def datatable_obj(self,request,columns,index_column,db,modal_obj,modal_filter):
        return DataTablesServer(request,columns,index_column,db,modal_obj,modal_filter)
        
    def validate_url(f):
        #Validate that client is trying to view only the sites owned by him
        @wraps(f)
        def decorated_function(*args, **kwargs):
            id =  request.view_args.get('id')
            if id is None:
                current_app.logger.debug("Unknown Site ID: %s "%(request.url))
                return jsonify({'status': 0,'msg':'Unknown Site ID'})
            #perform additional permission checks
            if not  current_app.config['LOGIN_DISABLED']:
                #check if site ID is owned by the client
                if not current_user.type == 'admin':
                    wifisite = Wifisite.query.filter_by(id=id).first()
                    if not wifisite:
                        current_app.logger.debug("Unknown Site ID: %s "%(request.url))
                        return jsonify({'status': 0,'msg':'Unknown Site ID'})
                    if not wifisite.client_id == current_user.id:
                        current_app.logger.debug("Client trying to access unauthorized URL %s "%(request.url))
                        return jsonify({'status': 0,'msg':'Not Authorized'})                  
            return f(*args, **kwargs)
        return decorated_function
    #
    #
    @validate_url   
    def get(self,id):   
        #create modal_filter with clientid and siteid       
        modal_filter ={'siteid':id}
        # return a list of all elements    
        results = self.datatable_obj(request, self.columns, self.index_column, db,self.get_modal_obj(),modal_filter).output_result()
        return jsonify(results) 

    @validate_url
    def post(self,clientid,siteid,id): 
        current_app.logger.debug("User with ID:%s is trying to access guestdata API with POST :%s "%(current_user.id,request.url))            
        abort(404)
    @validate_url
    def delete(self,clientid,siteid,id):   
        current_app.logger.debug("User with ID:%s is trying to access guestdata API with DELTE :%s "%(current_user.id,request.url))  
        abort(404)





class VoucherAPI(UnifispotAPI):

    ''' API class to deal with LandingPage entries
    
    '''
    def __init__(self):
        super(self.__class__, self).__init__()
        self.columns = ['site','voucher','duration','status','note']
        self.entity_name = 'Voucher'
        
    def get_template_name(self):
        return ''

    def get_modal_obj(self):
        return Voucher()

    def get_form_obj(self):
        return VoucherForm()

    def api_path(self):
        return '/clients/site/<int:siteid>/voucher/api/'
        
    def datatable_obj(self,request,columns,index_column,db,modal_obj,modal_filter):
        class VoucherDataTableServer(DataTablesServer):
            def __init__( self, request, columns, index,db,model,modal_filters):
                super(self.__class__, self).__init__(request, columns, index,db,model,modal_filters)            
            def custom_column(self,row):
                #function to add custom column if needed
                button_row = '''<a class="btn btn-red btn-sm delete" href="#" id="%s" alt="Delete">
                                <i class="fa fa-times"></i>Delete</a>'''%(row['id'])
                return button_row
        return VoucherDataTableServer(request,columns,index_column,db,modal_obj,modal_filter)
        
    def validate_url(f):
        #Validate that client is trying to view only the sites owned by him
        @wraps(f)
        def decorated_function(*args, **kwargs):
            id =  request.view_args.get('id')
            siteid =  request.view_args.get('siteid')  
            wifisite = Wifisite.query.filter_by(id=siteid).first()
            if not wifisite:
                current_app.logger.debug("Client  is trying to unknown site ID:%s "%(request.url))
                abort(404)   
            #admin user can have full access
            #perform additional permission checks
            if not  current_app.config['LOGIN_DISABLED']:
                if not current_user.check_admin() and wifisite.client_id != current_user.id:
                    return jsonify({'status': 0,'msg':'Not Authorized'}) 
                  
            return f(*args, **kwargs)
        return decorated_function
    #
    @validate_url   
    def get(self,siteid,id):   
        modal_filter ={'siteid':siteid}
        # return a list of all elements    
        results = self.datatable_obj(request, self.columns, self.index_column, db,Voucher(),modal_filter).output_result()
        return jsonify(results) 
    @validate_url
    def post(self,siteid,id):             
        if id is None:
        # create a new element
            form1 = self.get_form_obj()
            form1.populate()
            if  form1.validate_on_submit():                        
                wifisite = Wifisite.query.filter_by(id=siteid).first()
                #generate batch id
                batchid = str(uuid.uuid4())
                cnt = 0
                try:
                    while cnt < int(form1.number.data):  
                        cnt = cnt + 1  
                        newitem = self.get_modal_obj()   
                        newitem.populate_from_form(form1)          
                        #create voucher
                        random = randint(100, 999)  # randint is inclusive at both ends
                        hashid = Hashids(salt=current_app.config['HASH_SALT'],min_length=10)
                        newitem.voucher = hashid.encode(random,wifisite.id,wifisite.client_id)
                        newitem.batchid = batchid
                        newitem.site = wifisite                           
                        db.session.add(newitem)
                    db.session.commit()
                except :
                    current_app.logger.exception('Exception while trying create vouchers')
                    return jsonify({'status': 0,'msg':'Error while trying to create vouchers'})
                else:
                    return jsonify({'status': 1,'msg':'Added New Entry for:%s into Database'%self.entity_name})
            else:
                return jsonify({'status':0,'msg': get_errors(form1)})

        else:
            return jsonify({'status':0,'err': 'Voucher Editing is not allowed'})
    @validate_url
    def delete(self,siteid,id):     
        return super(VoucherAPI, self).delete(id)
                         
