SQLALCHEMY_DATABASE_URI = 'mysql://<user>:<password>@localhost/<db>'


#change 'unifispot.local' to domain of your choice
MAIL_DEFAULT_SENDER ='no-reply@unifispot.local'
SECURITY_EMAIL_SENDER = 'no-reply@unifispot.local'


#Email address of admin users
ADMINS = ['admin@unifispot.local']


DATA_INIT = True

HASH_SALT = 'HG6fgdtad67qtegdygdwuy'

FB_APP_SECRET = '<replace with FB APP SECRET>'
FB_APP_ID = '<replace with FB APP ID>'
FB_PAGE_URL = '<replace with fb page URL>'

##configuration to keep static files in S3
#UPLOAD_TO_S3 = False
#S3_ACCESS_KEY = ''
#S3_SECRET_KEY = ''
#S3_ENDPOINT   = ''
#S3_BUCKET     = ''



#need to chnage below only if redis is installed in a different server
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'



