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

manager.run()