from flask import jsonify,abort,request,current_app
from flask.ext.security import current_user
from sqlalchemy.exc import IntegrityError

from .models import Superadmin,Account
from .forms import AccountForm,AdminForm

from unifispot.base.api import UnifispotAPI
from unifispot.base.file import FileAPI
from unifispot.base.datatable import DataTablesServer
from unifispot.extensions import db
from unifispot.base.utils.forms import print_errors,get_errors
from unifispot.models import User,user_datastore,Role
from unifispot.base.utils.roles import superadmin_required
from unifispot.guest.models import Guest,Guestsession,Device,Guesttrack
from unifispot.client.models import Wifisite,Landingpage,Sitefile,Client,Voucher
from unifispot.admin.models import Admin

from functools import wraps


class AccountAPI(UnifispotAPI):

    ''' API class to deal with Account entries
    
    '''

    def __init__(self):
        super(self.__class__, self).__init__()
        self.columns = ['name','sites_allowed','expiresat','account_type']
        self.entity_name = 'Account Details'
        
    def get_modal_obj(self):
        return Account()

    def get_form_obj(self):
        return AccountForm()
      
    def datatable_obj(self,request,columns,index_column,db,modal_obj):
        return DataTablesServer(request,columns,index_column,db,modal_obj)

    @superadmin_required   
    def get(self,id):   
        return super(AccountAPI, self).get(id)

    @superadmin_required   
    def post(self,id):   
        return super(AccountAPI, self).post(id)

    @superadmin_required   
    def delete(self,id):   
        #delete all connected items
        try:
            #delete all sites and items related sites
            #Landing pages,Guest,Device,Guestsession,Guesttrack,Sitefile
            for site in Wifisite.query.filter_by(account_id=id).all():
                [db.session.delete(item) for item in Landingpage.query.filter_by(site_id=site.id).all()]
                [db.session.delete(item) for item in Landingpage.query.filter_by(site_id=site.id).all()]
                [db.session.delete(item) for item in Guest.query.filter_by(site_id=site.id).all()]
                [db.session.delete(item) for item in Device.query.filter_by(site_id=site.id).all()]
                [db.session.delete(item) for item in Guestsession.query.filter_by(site_id=site.id).all()]
                [db.session.delete(item) for item in Guesttrack.query.filter_by(site_id=site.id).all()]
                [db.session.delete(item) for item in Sitefile.query.filter_by(site_id=site.id).all()]
                [db.session.delete(item) for item in Voucher.query.filter_by(site_id=site.id).all()]
                db.session.delete(site)
            #delet clients and admins
            [db.session.delete(item) for item in Admin.query.filter_by(account_id=id).all()]
            [db.session.delete(item) for item in Client.query.filter_by(account_id=id).all()]
            db.session.commit()
        except:
            current_app.logger.exception('Exception while trying to delete account ID:%s'%id)
            return jsonify({'status':0,'err': 'Some Error Occured while processing:%s'%self.entity_name})
        return super(AccountAPI, self).delete(id)          


class AdminAPI(UnifispotAPI):
    ''' API class to deal with User entries
    
    '''
    def __init__(self):
        super(self.__class__, self).__init__()    
        self.columns = ['displayname','email','account']
        self.entity_name = 'Admin'

    def get_template_name(self):
        return None

    def get_modal_obj(self):
        return Admin()

    def get_form_obj(self):
        return AdminForm()

    def api_path(self):
        return None

    def datatable_obj(self,request,columns,index_column,db,modal_obj,modal_filter):
        return DataTablesServer(request,columns,index_column,db,modal_obj,modal_filter)

    @superadmin_required   
    def get(self,id):   
        if id is None:
            modal_filter =None
            # return a list of all elements    
            results = self.datatable_obj(request, self.columns, self.index_column, db,Admin(),modal_filter).output_result()
            return jsonify(results)          
        return super(AdminAPI, self).get(id)

    @superadmin_required   
    def post(self,id):    
        if id is None:
            form1 = self.get_form_obj()
            form1.populate()
            if  form1.validate_on_submit():
                account = Account.query.filter_by(id=form1.account.data).first()
                if not account:
                    return jsonify({'status': None,'err':'Invalid Account'})
                newitem = Admin()
                newitem.populate_from_form(form1)
                newitem.active = 1
                newitem.account = account
                db.session.commit()
                try:
                    db.session.add(newitem)
                    db.session.commit()
                except IntegrityError:
                    return jsonify({'status': None,'err':'Value already exists in the database'})
                return jsonify({'status': 1,'id':newitem.id})
            return jsonify({'status': 0,'err':get_errors(form1)})
        else:
            # update a single item
            singleitem = Admin.query.filter_by(id=id).first()
            if singleitem:
                form1 = self.get_form_obj()
                form1.populate()
                if form1.validate_on_submit():
                    singleitem.populate_from_form(form1)
                    singleitem.account_id = form1.account.data
                    try:
                        db.session.commit()
                    except IntegrityError:
                        return jsonify({'status': None,'err':'Value already exists in the database'})
                    return jsonify({'status': 1})
                else:
                    return jsonify({'status':0,'err': get_errors(form1)})
            return jsonify({'status':0,'err': 'unknown user'})     

    @superadmin_required   
    def delete(self,id): 
        return super(AdminAPI, self).post(id)