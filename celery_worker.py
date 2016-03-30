#! flask/bin/python
from os.path import abspath

from flask import current_app
from flask.ext.script import Manager
from flask.ext.assets import ManageAssets
from flask.ext.migrate import Migrate, MigrateCommand

from unifispot import create_app
from unifispot.extensions import celery
from unifispot import tasks



app = create_app(mode= 'development')
#solution to start fresh flask-sqlalchemy session on each task https://gist.github.com/twolfson/a1b329e9353f9b575131
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['CELERY_ALWAYS_EAGER'] = True
app.app_context().push()

import logging
from logging.handlers import RotatingFileHandler
log_file = '/usr/share/nginx/unifispot/logs/celery.log'
file_handler = RotatingFileHandler(log_file,'a', 1 * 1024 * 1024, 10)
app.logger.setLevel(logging.DEBUG)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
app.logger.addHandler(file_handler)

