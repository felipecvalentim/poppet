import os
from passlib.hash import sha256_crypt

#WTF
CSRF_ENABLED = True


#configure blue prints 

BLUEPRINTS = ('client','guest','admin')



#Configure DB
basedir = os.path.join(os.path.abspath(os.path.dirname(__file__)),'..','unifispot')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SECRET_KEY = '7ydhgq6et8721yehuaidhasid8a7sdh87asdh'

SECURITY_REGISTERABLE = False
SQLALCHEMY_DATABASE_URI = 'sqlite:///'+os.path.join(os.path.abspath(os.path.dirname(__file__)),'database.db')
SECURITY_PASSWORD_HASH = 'sha256_crypt'
SECURITY_PASSWORD_SALT = "AJSHASJHAJSHASJHSAJHASJAHSJAHJSA"



#SQLALCHEMY_ECHO = True
STATIC_FILES = os.path.join(basedir,'static')

SITE_FILE_UPLOAD = 'uploads'
BASE_FOLDER = os.path.join(basedir,'static')

#SQLALCHEMY_ECHO = True
ASSETS_DEBUG = True 
DEBUG = False

DATA_INIT = False
NO_UNIFI = False

LOGIN_DISABLED = False

SECURITY_UNAUTHORIZED_VIEW = '/login'
SECURITY_POST_LOGIN_VIEW = '/'
SECURITY_POST_LOGOUT_VIEW = '/login'
SECURITY_RECOVERABLE = True

SECURITY_MSG_INVALID_PASSWORD = ("Bad username or password", "error")
SECURITY_MSG_PASSWORD_NOT_PROVIDED = ("Bad username or password", "error")
SECURITY_MSG_USER_DOES_NOT_EXIST = ("Bad username or password", "error")
SECURITY_TOKEN_MAX_AGE = 1800
SECURITY_TRACKABLE = True



MAIL_EXCEPTION_THROTTLE = 5


SQLALCHEMY_COMMIT_ON_TEARDOWN =False
CELERY_ALWAYS_EAGER = False
#http://primalpappachan.com/devops/2013/07/30/aws-rds--mysql-server-has-gone-away/
#--Fix for aws-rds-server has gone away
SQLALCHEMY_POOL_RECYCLE = 3600

##not going to use server side sessions
#Flask-session configuration for server side session handling
SESSION_TYPE = 'sqlalchemy'


#S3 file upload
UPLOAD_TO_S3 = False
