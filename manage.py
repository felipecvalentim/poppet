#! flask/bin/python
from os.path import abspath

from flask import current_app
from flask.ext.script import Manager
from flask.ext.assets import ManageAssets
from flask.ext.migrate import Migrate, MigrateCommand

from unifispot import create_app
from unifispot.extensions import db


app = create_app(mode='development')
manager = Manager(app)
manager.add_command('assets', ManageAssets())
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)


#app.run(host='0.0.0.0',debug = True)
@manager.command
def init_data():
    with app.app_context():
        from  sqlalchemy.exc import OperationalError    
        from flask.ext.security.utils import encrypt_password
        from unifispot.models import User  
        from unifispot.superadmin.models import Account
        from unifispot.admin.models import Admin       
        try:
            account = Account.query.filter_by(id=1).first()
        except :
            app.logger.debug( "No Account table Entry found,could be running migration ")
        else:
            if not account:
                #create default admin user
                enc_pass        = encrypt_password('password')
                account         = Account()
                db.session.add(account)
                admin_user = Admin(email='admin@admin.com',password=enc_pass,displayname= "Admin User",active=1)
                admin_user.account = account
                db.session.add(admin_user)
                db.session.commit()

@manager.command
def demo_init():
    with app.app_context():
        from  sqlalchemy.exc import OperationalError    
        from flask.ext.security.utils import encrypt_password
        from unifispot.models import User  
        from unifispot.superadmin.models import Account,Superadmin
        from unifispot.admin.models import Admin       
        from unifispot.client.models import Client       
        try:
            account = Account.query.filter_by(id=1).first()
        except :
            app.logger.debug( "No Account table Entry found,could be running migration ")
        else:
            if not account:
                #create default admin user
                enc_pass        = encrypt_password('password')
                account         = Account()
                db.session.add(account)
                super_admin = Superadmin(email='super@unifispot.com',password=enc_pass,displayname= "Super Admin",active=1)
                admin_user  = Admin(email='admin@admin.com',password=enc_pass,displayname= "Admin User1",active=1)
                admin_user2 = Admin(email='admin2@admin.com',password=enc_pass,displayname= "Admin User2",active=1)
                admin_user3 = Admin(email='admin3@admin.com',password=enc_pass,displayname= "Admin User3",active=1)
                admin_user.account = account
                admin_user2.account = account
                admin_user3.account = account
                db.session.add(super_admin)
                db.session.add(admin_user)
                db.session.add(admin_user2)
                db.session.add(admin_user3)
                db.session.commit()

@manager.command
def demo_superadmin():
    with app.app_context():
        from  sqlalchemy.exc import OperationalError    
        from flask.ext.security.utils import encrypt_password
        from unifispot.models import User  
        from unifispot.superadmin.models import Account,Superadmin
        from unifispot.admin.models import Admin       
        from unifispot.client.models import Client   
        #create default admin user
        enc_pass        = encrypt_password('password')
        super_admin = Superadmin(email='super@unifispot.com',password=enc_pass,displayname= "Super Admin",active=1)
        db.session.add(super_admin)
        db.session.commit()        

manager.run()