from flask import render_template,redirect,url_for,Flask,Config,abort
from flask.ext.security import Security,SQLAlchemyUserDatastore
from flask.ext.security import login_required,current_user
from flask.ext.assets import Environment
import re
#import basic utlities
from base.utils.core import (load_blueprint_settings, load_blueprints,error_handler,)
#import bundles
from assets import bundles
import os
import yaml
from unifispot.extensions import db,mail,celery,redis
from unifispot.admin.models import Admin       
from unifispot.superadmin.models import Account       
from unifispot.client.models import Client      

def create_app(mode="development"):
    """Create webapp instance."""
    app = Flask(__name__,instance_relative_config=True)
    #Load database

    #Initilise DB

    from unifispot.models import user_datastore
    db.init_app(app)


    # Load the default configuration
    app.config.from_object('config.default')

    # Load the configuration from the instance folder
    app.config.from_pyfile('config.py')
 

    # Load the file specified by the config_filename environment variable
    # Variables defined here will override those in the default configuration
    if mode is not None:
        app.config.from_object('config.'+mode)
        # Load test database config
        if mode == 'testing':
            app.config.from_pyfile('config_test.py')
        elif mode == 'e2e_testing':
            app.config.from_pyfile('config_e2e_test.py')        
    #Setup Flask-Security before loading any blueprints
    security = Security(app, user_datastore)   
    #initilise mail,celery and redis

    mail.init_app(app)
    celery.init_app(app)   
    redis.init_app(app)   
    ##not going to use server side sessions
    #sess.init_app(app)

    #initlize assets
    assets = Environment(app)
    assets.register(bundles)    
    # simple load all blueprint settings, enabled in config
    load_blueprint_settings(app,blueprint_path='unifispot')

    # simple load all blueprints, enabled in config
    load_blueprints(app,blueprint_path='unifispot')

    #check for default values required before starting app
    with app.app_context():
        from importlib import import_module
        import_module('unifispot.middleware')

                   

    @app.route("/")
    @login_required
    def home():
        if current_user.type =='admin':
            return redirect(url_for('admin.admin_index'))
        elif current_user.type =='client':
            return redirect(url_for('client.client_index'))     
        elif current_user.type =='superadmin':
            return redirect(url_for('superadmin.superadmin_index'))               
        else:
            app.logger.error("Unknown User Type!! for ID:%s"%current_user.id)
            abort(400)

    return app

