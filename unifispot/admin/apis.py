from flask import jsonify,abort,request,current_app
from flask.ext.security import current_user,login_required
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_,or_
from .models import Admin
from .forms import SettingsForm,UserForm
from unifihelper import ap_status_generate,guest_status_generate
from .controller import Controller 

from unifispot.base.api import UnifispotAPI
from unifispot.base.datatable import DataTablesServer

from unifispot.extensions import db
from unifispot.base.utils.forms import print_errors,get_errors
from unifispot.models import User,user_datastore,Role
from unifispot.guest.models import Guest,Guestsession,Device,Guesttrack,Facebookauth
from unifispot.client.models import Wifisite,Client
from unifispot.admin.models import Admin
from unifispot.superadmin.models import Account
from unifispot.const import ROLE_ADMIN,ROLE_CLIENT
from unifispot.base.utils.roles import admin_required

from functools import wraps
from urlparse import urlparse


class SettingsAPI(UnifispotAPI):


    ''' API class to deal with LandingPage entries
    
    '''
    def __init__(self):
        super(self.__class__, self).__init__()
        
    def get_template_name(self):
        return NotImplementedError

    def get_modal_obj(self):
        return Account()

    def get_form_obj(self):
        return SettingsForm()

    def api_path(self):
        return '/admin/settings/api/'
        
    def datatable_obj(self):
        return NotImplementedError
        
    def validate_url(f):
        #Validate 
        @wraps(f)
        def decorated_function(*args, **kwargs):
            id =  request.view_args.get('id')
            #perform additional permission checks
            if not  current_app.config['LOGIN_DISABLED'] :
                if not current_user.check_admin():
                    return jsonify({'status': 0,'msg':'Not Authorized'}) 
            return f(*args, **kwargs)
        return decorated_function
    #
    #
    @validate_url   
    def get(self,id): 
        singleitem = Account().query.filter_by(id=current_user.account_id).first()
        if singleitem:
            return jsonify({'status': 1,'data':singleitem.get_settings()})
        else:
            current_app.logger.debug("No Settings Entry in Settings table!! %s "%(request.url))  
            return jsonify({'status': 0,'msg':'No Settings Entry Found'})

    @validate_url
    def post(self,id): 
        singleitem = Account().query.filter_by(id=current_user.account_id).first()
        form1 = self.get_form_obj()
        form1.populate()
        if  form1.validate_on_submit(): 
            singleitem.populate_settings(form1)
            try:
                db.session.commit()
            except IntegrityError:
                return jsonify({'status': 0,'msg':'Value already exists in the database'})
            return jsonify({'status': 1})
        else:
            return jsonify({'status':0,'msg': get_errors(form1)})
    @validate_url
    def delete(self,id):   
        current_app.logger.debug("user trying to delete Settings Entry!! %s"%(request.url))  
        return jsonify({'status': 0,'msg':'Not Allowed'})



class AdminAPI(UnifispotAPI):
    ''' API class to deal with User entries
    
    '''
    def __init__(self):
        super(self.__class__, self).__init__()    
        self.columns = ['displayname','email']
        self.entity_name = 'Admin'

    def get_template_name(self):
        return None

    def get_modal_obj(self):
        return Admin()

    def get_form_obj(self):
        return UserForm()

    def api_path(self):
        return None

    def datatable_obj(self,request,columns,index_column,db,modal_obj,modal_filter):
        return DataTablesServer(request,columns,index_column,db,modal_obj,modal_filter)

    def validate_url(f):
        #Validate 
        @wraps(f)
        def decorated_function(*args, **kwargs):
            id =  request.view_args.get('id')
            #perform additional permission checks
            if not  current_app.config['LOGIN_DISABLED'] :
                if not current_user.check_admin():
                    return jsonify({'status': 0,'msg':'Not Authorized'}) 
                if id :
                    admin = Admin.query.filter_by(id=id).first()
                    if not admin or admin.account_id != current_user.account_id:
                        current_app.logger.error("User ID:%s trying to access unauthorized Admin:%s URL:%s"%(current_user.id,id,request.url))
                        return jsonify({'status': 0,'msg':'Not Authorized'}) 
                    
            return f(*args, **kwargs)
        return decorated_function
    #
    #
    @validate_url   
    def get(self,id): 
        if id is None:
            modal_filter ={'account_id':current_user.account_id}
            # return a list of all elements    
            results = self.datatable_obj(request, self.columns, self.index_column, db,Admin(),modal_filter).output_result()
            return jsonify(results)          
        else:
            #Returns a single element
            singleitem = Admin.query.filter_by(id=id).first()
            if singleitem:
                return jsonify({'status':1,'data':singleitem.to_dict(),'msg':'Successfully returning :%s'%self.entity_name})
            else:
                return jsonify({'status':0,'msg':'Invalid ID Specified for %s'%self.entity_name})

    @validate_url
    def post(self,id): 
        account = Account.query.filter_by(id=current_user.account_id).first()
        if not account:
            return jsonify({'status': 0,'msg':'Not  Valid Account ID'})         
        if id is None:
            # create a new element
            form1 = self.get_form_obj()
            form1.populate()
            if  form1.validate_on_submit():
                try:
                    newitem = Admin()
                    newitem.populate_from_form(form1)
                    newitem.active = 1
                    newitem.account = account
                    db.session.add(newitem)
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()
                    db.session.flush() # for resetting non-commited .add()
                    current_app.logger.error('Trying to add duplicate Admin Account with email:%s'%newitem.email)
                    return jsonify({'status': 0,'msg':'Value already exists in the database'})
                else:
                    return jsonify({'status': 1,'id':newitem.id})
            return jsonify({'status': 0,'msg':get_errors(form1)})
        else:
            # update a single item
            singleitem = Admin.query.filter_by(id=id).first()
            if singleitem:
                form1 = self.get_form_obj()
                form1.populate()
                if form1.validate_on_submit():
                    singleitem.populate_from_form(form1)
                    try:
                        db.session.commit()
                    except IntegrityError:
                        return jsonify({'status': None,'msg':'Value already exists in the database'})
                    return jsonify({'status': 1})
                else:
                    return jsonify({'status':0,'msg': get_errors(form1)})
            return jsonify({'status':0,'msg': 'unknown user'})            
    @validate_url
    def delete(self,id):   
        singleitem = Admin.query.filter_by(id=id).first()
        if id is None or id == current_user.id or not singleitem :
            return jsonify({'status': 0,'msg':'Not Authorized'})   
        else:
            db.session.delete(singleitem)
            db.session.commit()
        return jsonify({'status': 1,'msg':'Admin Deleted'}) 




class ClientAPI(UnifispotAPI):
    ''' API class to deal with User entries
    
    '''
    def __init__(self):
        super(self.__class__, self).__init__()    
        self.columns = ['displayname','email']
        self.entity_name = 'Client'

    def get_template_name(self):
        return None

    def get_modal_obj(self):
        return Client()

    def get_form_obj(self):
        return UserForm()

    def api_path(self):
        return None

    def datatable_obj(self,request,columns,index_column,db,modal_obj,modal_filter):
        return DataTablesServer(request,columns,index_column,db,modal_obj,modal_filter)

    def validate_url(f):
        #Validate 
        @wraps(f)
        def decorated_function(*args, **kwargs):
            id =  request.view_args.get('id')
            #perform additional permission checks
            if not  current_app.config['LOGIN_DISABLED'] :
                if not current_user.check_admin():
                    return jsonify({'status': 0,'msg':'Not Authorized'}) 
                if id:
                    client = Client.query.filter_by(id=id).first()
                    if not client or client.account_id != current_user.account_id:
                        current_app.logger.error("Admin User ID:%s trying to access unauthorized client:%s URL:%s"%(current_user.id,id,request.url))
                        return jsonify({'status': 0,'msg':'Not Authorized'}) 
                    
            return f(*args, **kwargs)
        return decorated_function
    #
    #
    @validate_url   
    def get(self,id): 
        if id is None:
            modal_filter ={'account_id':current_user.account_id}
            # return a list of all elements    
            results = self.datatable_obj(request, self.columns, self.index_column, db,Client(),modal_filter).output_result()
            return jsonify(results)          
        else:
            #Returns a single element
            singleitem = Client.query.filter_by(id=id).first()
            if singleitem:
                return jsonify({'status':1,'data':singleitem.to_dict(),'msg':'Successfully returning :%s'%self.entity_name})
            else:
                return jsonify({'status':0,'msg':'Invalid ID Specified for %s'%self.entity_name})

    @validate_url
    def post(self,id): 
        account = Account.query.filter_by(id=current_user.account_id).first()

        if not account:
            return jsonify({'status': 0,'msg':'Not  Valid Account ID'})             
        if id is None:

            # create a new element
            form1 = self.get_form_obj()
            form1.populate()
            if  form1.validate_on_submit():
                try:
                    newitem = Client()
                    newitem.populate_from_form(form1)
                    newitem.active = 1
                    newitem.account = account
                    db.session.commit()               
                    
                    db.session.commit()
                except IntegrityError:
                    return jsonify({'status': 0,'msg':'Value already exists in the database'})
                return jsonify({'status': 1,'id':newitem.id})
            return jsonify({'status': 0,'msg':get_errors(form1)})
        else:
            # update a single item
            singleitem = Client.query.filter_by(id=id).first()
            if singleitem:
                form1 = self.get_form_obj()
                form1.populate()
                if form1.validate_on_submit():
                    singleitem.populate_from_form(form1)
                    try:
                        db.session.commit()
                    except IntegrityError:
                        return jsonify({'status': None,'msg':'Value already exists in the database'})
                    return jsonify({'status': 1})
                else:
                    return jsonify({'status':0,'msg': get_errors(form1)})
            return jsonify({'status':0,'msg': 'unknown user'})            
    @validate_url
    def delete(self,id):   
        singleitem = User.query.filter_by(id=id).first()
        if id == current_user.id or not singleitem :
            return jsonify({'status': 0,'msg':'Not Authorized'})   
        try:      
            if singleitem:
                #delete all the wifisites and stored data
                def delete_all(datas):
                    for data in datas:
                        db.session.delete(data)
                client = Client.query.filter_by(id=id).first()
                sites = Wifisite.query.filter_by(client_id=client.id).all()
                for site in sites:
                    delete_all(Guest.query.filter_by(site_id=site.id).all())
                    delete_all(Device.query.filter_by(site_id=site.id).all())
                    delete_all(Guestsession.query.filter_by(site_id=site.id).all())
                    delete_all(Guesttrack.query.filter_by(site_id=site.id).all())
                    delete_all(Facebookauth.query.filter_by(site_id=site.id).all())
                    db.session.delete(site)
                db.session.delete(client)
                db.session.delete(singleitem)
                db.session.commit()
                
            else:
                return jsonify({'status': 0,'msg':'Unknown CLient ID'})  

        except:
            current_app.logger.exception("Exception while trying to delete a client :%s by admin:%s"%(request.url,current_user.id))
            return jsonify({'status': 0,'msg':'Some error occured while trying to delete the client'})  
        else:
            return jsonify({'status': 1,'msg':'Successfuly deleted the client'}) 


class UserAPI(UnifispotAPI):
    ''' API class to deal with User entries
    
    '''
    def __init__(self):
        super(self.__class__, self).__init__()    
        self.columns = ['displayname','email','usertype']
        self.entity_name = 'Client'

    def get_template_name(self):
        return None

    def get_modal_obj(self):
        return User()

    def get_form_obj(self):
        return UserForm()

    def api_path(self):
        return None

    def datatable_obj(self,request,columns,index_column,db,modal_obj,modal_filter):
        return NotImplementedError

    def validate_url(f):
        #Validate 
        @wraps(f)
        def decorated_function(*args, **kwargs):
            id =  request.view_args.get('id')
            #perform additional permission checks
            if not  current_app.config['LOGIN_DISABLED'] and id != current_user.id :
                return jsonify({'status': 0,'msg':'Not Authorized'})                     
            return f(*args, **kwargs)
        return decorated_function
    #
    #
    @validate_url   
    def get(self,id): 
        if id is None:
             return jsonify({'status': 0,'msg':'Not Authorized'})           
        else:
            #Returns a single element
            singleitem = User.query.filter_by(id=id).first()
            if singleitem:
                return jsonify({'status':1,'data':singleitem.to_dict(),'msg':'Successfully returning :%s'%self.entity_name})
            else:
                return jsonify({'status':0,'msg':'Invalid ID Specified for %s'%self.entity_name})

    @validate_url
    def post(self,id): 
        if id is None:
             return jsonify({'status': 0,'msg':'Not Authorized'})    
        else:
            # update a single item
            singleitem = User.query.filter_by(id=id).first()
            if singleitem:
                form1 = self.get_form_obj()
                form1.populate()
                if form1.validate_on_submit():
                    singleitem.populate_from_form(form1)
                    try:
                        db.session.commit()
                    except IntegrityError:
                        return jsonify({'status': None,'msg':'Value already exists in the database'})
                    return jsonify({'status': 1})
                else:
                    print  form1.errors
                    return jsonify({'status':0,'msg': get_errors(form1)})
            return jsonify({'status':0,'msg': 'unknown user'})            
    @validate_url
    def delete(self,id):   
        return jsonify({'status': 0,'msg':'Not Authorized'}) 



class AccesspointAPI(UnifispotAPI):
    ''' API class to deal with APs
    
    '''
    def __init__(self):
        super(self.__class__, self).__init__()    

    def get_template_name(self):
        return None

    def get_modal_obj(self):
        return None

    def get_form_obj(self):
        return None

    def api_path(self):
        return None

    def validate_url(f):
        #Validate 
        @wraps(f)
        def decorated_function(*args, **kwargs):
            id =  request.view_args.get('id')
            #perform additional permission checks
            if not  current_app.config['LOGIN_DISABLED'] :
                if id :
                    wifisite = Wifisite.query.filter_by(id=id).first()
                    if  wifisite.account_id != current_user.account_id:
                        current_app.logger.error("User ID:%s trying to access unauthorized AP API ID:%s URL:%s"%(current_user.id,id,request.url))
                        return jsonify({'status': 0,'msg':'Not Authorized'}) 
                    
            return f(*args, **kwargs)
        return decorated_function
    #
    @validate_url     
    def get(self,id): 
        ap_list = []
        if not id:
            #get all APs status
            if not current_app.config['NO_UNIFI']:
                
                account = Account().query.filter_by(id=current_user.account_id).first()
                settings = account.get_settings()
                if not settings:
                    current_app.logger.debug("No Settings Entry in User table!! %s "%(request.url))  
                    return jsonify({'status': 0,'msg':'Error while loading settings'})
                else:
                    c = Controller(settings['unifi_server'], settings['unifi_user'], settings['unifi_pass'],version='v4',site_id='default')
                if current_user.type =='admin':
                    sites = Wifisite.query.filter_by(account_id=current_user.account_id).all()
                elif current_user.type =='client':
                    sites = Wifisite.query.filter_by(client_id=current_user.id).all()
                if sites:
                    for site in sites:
                        site_aps = c.get_aps(site_id=site.unifi_id)
                        for site_ap in site_aps:
                            ap_list.append([site_ap.get('mac'),site_ap.get('name'),site.name,ap_status_generate(site_ap.get('state'))])
            else:
                ap_list = [['11:22:33:44:55:66',"AP1",'SITE1','<span class="label label-success">AP Active</span>'],['11:22:33:44:55:66',"AP4",'SITE4',ap_status_generate(2)],['11:22:33:44:55:66',"AP1",'SIT31',ap_status_generate(1)],['11:22:33:44:55:66',"AP1",'SITE1',ap_status_generate(1)]]

        else:
           
            if not current_app.config['NO_UNIFI']:

                account = Account().query.filter_by(id=current_user.account_id).first()
                settings = account.get_settings()
                if current_user.type =='admin':
                    wifisite = Wifisite.query.filter(and_(Wifisite.id==id,Wifisite.account_id==current_user.account_id)).first()
                elif current_user.type =='client':
                    wifisite = Wifisite.query.filter(and_(Wifisite.id==id,Wifisite.client_id==current_user.id)).first()

                if not settings:
                    current_app.logger.debug("No Settings Entry in User table!! %s "%(request.url))  
                    return jsonify({'status': 0,'msg':'Error while loading settings'})
                if wifisite:
                    c = Controller(settings['unifi_server'], settings['unifi_user'], settings['unifi_pass'],version='v4',site_id='default')
                    site_aps = c.get_aps(site_id=wifisite.unifi_id)
                    for site_ap in site_aps:
                        ap_list.append([site_ap.get('mac'),site_ap.get('name'),wifisite.name,ap_status_generate(site_ap.get('state'))])
            else:
                ap_list = [['11:22:33:44:55:66',"AP1",'SITE1',ap_status_generate(1)],['11:22:33:44:55:66',"AP4",'SITE4',ap_status_generate(2)],['11:22:33:44:55:66',"AP1",'SIT31',ap_status_generate(1)],['11:22:33:44:55:66',"AP1",'SITE1',ap_status_generate(1)]]
        return jsonify({'status': 1,'data':ap_list})

    @validate_url  
    def post(self,id): 
        return jsonify({'status': 0,'msg':'Not Allowed'})
    @validate_url  
    def delete(self,id):   
        current_app.logger.debug("user trying to delete User Entry!! %s"%(request.url))  
        return jsonify({'status': 0,'msg':'Not Allowed'})




class DevicesAPI(UnifispotAPI):
    ''' API class to deal with APs
    
    '''
    def __init__(self):
        super(self.__class__, self).__init__()    

    def get_template_name(self):
        return None

    def get_modal_obj(self):
        return None

    def get_form_obj(self):
        return None

    def api_path(self):
        return None


    def validate_url(f):
        #Validate 
        @wraps(f)
        def decorated_function(*args, **kwargs):
            id =  request.view_args.get('id')
            #perform additional permission checks
            if not  current_app.config['LOGIN_DISABLED'] :
                if id :
                    wifisite = Wifisite.query.filter_by(id=id).first()
                    if  wifisite.account_id != current_user.account_id:
                        current_app.logger.error("User ID:%s trying to access unauthorized AP API ID:%s URL:%s"%(current_user.id,id,request.url))
                        return jsonify({'status': 0,'msg':'Not Authorized'})                     
            return f(*args, **kwargs)
        return decorated_function 
    #
    @validate_url   
    def get(self,id): 
        client_list = []
        if not id:
            #get all APs status
            if not current_app.config['NO_UNIFI']:
                account = Account().query.filter_by(id=current_user.account_id).first()
                settings = account.get_settings()
                if not settings:
                    current_app.logger.debug("No Settings Entry in User table!! %s "%(request.url))  
                    return jsonify({'status': 0,'msg':'Error while loading settings'})
                else:
                    c = Controller(settings['unifi_server'], settings['unifi_user'], settings['unifi_pass'],version='v4',site_id='default')
                if current_user.type =='admin':
                    sites = Wifisite.query.filter_by(account_id=current_user.account_id).all()
                elif current_user.type =='client':
                    sites = Wifisite.query.filter_by(client_id=current_user.id).all() 
                if sites:                   
                    c = Controller(settings['unifi_server'], settings['unifi_user'], settings['unifi_pass'],version='v4',site_id='default')
                    for site in sites:
                        site_clients = c.get_clients(site_id=site.unifi_id)
                        for site_client in site_clients:
                            if site_client.get('is_guest'):
                                client_list.append(guest_status_generate(site_client,site.name))
            else:
                client_list = [['SITE1','11:22:33:44:55:66','11:22:33:44:55:66',"40",'00:41','<span class="label label-success">Authorized</span>'],['SITE1','11:22:33:44:55:66','11:22:33:44:55:66',"40",'00:41','<span class="label label-success">Authorized</span>'],['SITE1','11:22:33:44:55:66','11:22:33:44:55:66',"40",'00:41','<span class="label label-success">Authorized</span>']]

        else:
            if not current_app.config['NO_UNIFI']:
                account = Account().query.filter_by(id=current_user.account_id).first()
                settings = account.get_settings()
                wifisite = Wifisite.query.filter_by(id=id).first()
                if not settings:
                    current_app.logger.debug("No Settings Entry in User table!! %s "%(request.url))  
                    return jsonify({'status': 0,'msg':'Error while loading settings'})
                if current_user.type =='admin':
                    wifisite = Wifisite.query.filter(and_(Wifisite.id==id,Wifisite.account_id==current_user.account_id)).first()
                elif current_user.type =='client':
                    wifisite = Wifisite.query.filter(and_(Wifisite.id==id,Wifisite.client_id==current_user.id)).first()
                if wifisite:
                    c = Controller(settings['unifi_server'], settings['unifi_user'], settings['unifi_pass'],version='v4',site_id='default')
                    site_clients = c.get_clients(site_id=wifisite.unifi_id)
                    for site_client in site_clients:
                         if site_client.get('is_guest'):
                            client_list.append(guest_status_generate(site_client,wifisite.name))
            else:
                client_list = [['SITE1','11:22:33:44:55:66','11:22:33:44:55:66',"40",'00:41','<span class="label label-success">Authorized</span>'],['SITE1','11:22:33:44:55:66','11:22:33:44:55:66',"40",'00:41','<span class="label label-success">Authorized</span>'],['SITE1','11:22:33:44:55:66','11:22:33:44:55:66',"40",'00:41','<span class="label label-success">Authorized</span>']]
        return jsonify({'status': 1,'data':client_list})

    @validate_url   
    def post(self,id): 
        return jsonify({'status': 0,'msg':'Not Allowed'})
    @validate_url   
    def delete(self,id):   
        return jsonify({'status': 0,'msg':'Not Allowed'})

