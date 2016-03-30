from functools import wraps
from flask import redirect,url_for,abort,current_app,request
from flask.ext.security import current_user
from datetime import datetime,date, timedelta
import time 

def client_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not  current_app.config['LOGIN_DISABLED']: 
            siteid =  request.view_args.get('siteid')       
            if not current_user.is_authenticated:
                current_app.logger.debug("Client URL :%s called by a user not logged in"%request.url)
                return redirect(url_for('security.login', next=request.url))
            if not current_user.type =='client':
                current_app.logger.debug("Client URL :%s called by a userID :%s who is not a client "%(request.url,current_user.id))
                return abort(401)           
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not  current_app.config['LOGIN_DISABLED']:      
            if not current_user.is_authenticated:
                current_app.logger.debug("Admin URL :%s called by a user not logged in"%request.url)
                return redirect(url_for('security.login', next=request.url))
            if not current_user.type =='admin':
                current_app.logger.debug("Admin URL :%s called by a userID :%s who is not an admin "%(request.url,current_user.id))
                return abort(401)
        return f(*args, **kwargs)
    return decorated_function    

def superadmin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not  current_app.config['LOGIN_DISABLED']:      
            if not current_user.is_authenticated:
                current_app.logger.debug("Super Admin URL :%s called by a user not logged in"%request.url)
                return redirect(url_for('security.login', next=request.url))
            if not current_user.type =='superadmin':
                current_app.logger.debug("Super Admin URL :%s called by a userID :%s who is not an superadmin "%(request.url,current_user.id))
                return abort(401)
        return f(*args, **kwargs)
    return decorated_function    