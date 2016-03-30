from flask import Blueprint,render_template,jsonify,request,current_app,abort
from flask.ext.security import login_required,current_user,roles_accepted
from unifispot.extensions import db
from functools import wraps
from unifispot.base.utils.helper import register_api
from unifispot.base.utils.roles import client_required
from sqlalchemy import and_,or_
from .apis import WifisiteAPI,SiteFileAPI,LandingPageAPI,GuestdataAPI,VoucherAPI
#
from .models import Wifisite,Landingpage,Sitefile,Voucher
from .forms import WifiSiteForm,LandingPageForm,VoucherForm

from unifispot.admin.forms import UserForm
from unifispot.guest.models import Guesttrack,Guest,Device

bp = Blueprint('client', __name__,template_folder='templates')


register_api(bp,WifisiteAPI,'wifisite_api','/site/api/',login_required)
register_api(bp,SiteFileAPI,'sitefile_api','/site/<int:siteid>/file/api/',login_required)
register_api(bp,LandingPageAPI,'landingpage_api','/site/<int:siteid>/landing/api/',login_required)
register_api(bp,VoucherAPI,'voucher_api','/site/<int:siteid>/voucher/api/',login_required)
register_api(bp,GuestdataAPI,'guestdata_api','/guestdata/api/',login_required)





@bp.route('/')
@bp.route('/<siteid>')
@client_required
def client_index(siteid=None):

    #Validate SiteID
    if not siteid:
        wifisite        = Wifisite.query.filter_by(client_id=current_user.id).first()
        siteid          = wifisite.id
    else:
        wifisite        = Wifisite.query.filter_by(id=siteid).first()
        if not wifisite or wifisite.client_id != current_user.id:
            current_app.logger.debug("Site Manage URL called with invalid paramters siteid:%s userid:%s"%(siteid,current_user.id))
            abort(404)

    site_count = Wifisite.query.filter_by(client_id=current_user.id).count()
    visit_count = Guesttrack.query.filter_by(site_id=wifisite.id).count()
    user_form = UserForm()
    site_form = WifiSiteForm()
    site_form.populate()
    
    return render_template("client/dashboard.html",siteid=siteid,user_form=user_form,site_form=site_form,site_count=site_count,visit_count=visit_count,wifisite=wifisite)


@bp.route('/')
@bp.route('/<siteid>')
@client_required
def client_settings(siteid=None):
    #Validate SiteID
    if not siteid:
        wifisite        = Wifisite.query.filter_by(client_id=current_user.id).first()
        siteid          = wifisite.id
    else:
        wifisite        = Wifisite.query.filter_by(id=siteid).first()
        if not wifisite or wifisite.client_id != current_user.id:
            current_app.logger.debug("Site Manage URL called with invalid paramters siteid:%s userid:%s"%(siteid,current_user.id))
            abort(404)

    user_form = UserForm()
    
    return render_template("client/dashboard.html",siteid=siteid,user_form=user_form,wifisite=wifisite)


  
@bp.route('/guestdata')
@bp.route('/guestdata/<siteid>')
@client_required
def client_data(siteid=None):
    #Validate SiteID
    if not siteid:
        wifisite        = Wifisite.query.filter_by(client_id=current_user.id).first()
        siteid          = wifisite.id
    else:
        wifisite        = Wifisite.query.filter_by(id=siteid).first()
        if not wifisite or wifisite.client_id != current_user.id:
            current_app.logger.debug("Site Manage URL called with invalid paramters siteid:%s userid:%s"%(siteid,current_user.id))
            abort(404)
    
    user_form = UserForm()
    
    return render_template("client/data.html",siteid=siteid,user_form=user_form,wifisite=wifisite)
  

@bp.route('/vouchers')
@bp.route('/vouchers/<siteid>')
@client_required
def client_vouchers(siteid=None):
    #Validate SiteID
    if not siteid:
        wifisite        = Wifisite.query.filter_by(client_id=current_user.id).first()
        siteid          = wifisite.id
    else:
        wifisite        = Wifisite.query.filter_by(id=siteid).first()
        if not wifisite or wifisite.client_id != current_user.id:
            current_app.logger.debug("Site Manage URL called with invalid paramters siteid:%s userid:%s"%(siteid,current_user.id))
            abort(404)
    
    user_form = UserForm()
    voucher_form = VoucherForm()
    voucher_form.populate()
    
    return render_template("client/vouchers.html",siteid=siteid,user_form=user_form,wifisite=wifisite,voucher_form=voucher_form)


@bp.route('/vouchers/<siteid>/print')
@client_required
def client_print(siteid=None):
    #Validate SiteID
    wifisite        = Wifisite.query.filter_by(id=siteid).first()
    if not wifisite or wifisite.client_id != current_user.id:
        current_app.logger.debug("Site Manage URL called with invalid paramters siteid:%s userid:%s"%(siteid,current_user.id))
        abort(404)
    vouchers = Voucher.query.filter(and_(Voucher.site_id==siteid,Voucher.used == False)).all()
    print vouchers
    return render_template("client/print.html",vouchers=vouchers)