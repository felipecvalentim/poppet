from flask import Blueprint,render_template,jsonify,request,current_app,abort
from flask.ext.security import login_required,current_user,roles_accepted
from unifispot.extensions import db
from functools import wraps
from unifispot.base.utils.helper import register_api
from .models import Superadmin
from .forms import UserForm,AccountForm,AdminForm
from .apis import AccountAPI,AdminAPI
from unifispot.base.utils.roles import superadmin_required

bp = Blueprint('superadmin', __name__,template_folder='templates')

register_api(bp,AccountAPI,'accounts_api','/accounts/api/',superadmin_required)
register_api(bp,AdminAPI,'admin_api','/admins/api/',superadmin_required)


@bp.route('/')
@superadmin_required
def superadmin_index( ):
    user_form = UserForm()
    return render_template('superadmin/dashboard.html',user_form=user_form)



@bp.route('/accounts')
@superadmin_required
def superadmin_accounts( ):
    user_form = UserForm()
    account_form = AccountForm()
    account_form.populate()
    return render_template('superadmin/accounts.html',user_form=user_form,account_form=account_form)


@bp.route('/admins')
@superadmin_required
def superadmin_admins( ):
    user_form = UserForm()
    admin_form = AdminForm()
    admin_form.populate()    
    return render_template('superadmin/admins.html',user_form=user_form,admin_form=admin_form)