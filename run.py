#! flask/bin/python
from os.path import abspath

from flask import current_app
from flask.ext.script import Manager
from flask.ext.assets import ManageAssets
from flask.ext.migrate import Migrate, MigrateCommand

from unifispot import create_app
from unifispot.extensions import db,mail,celery,redis


app = create_app(mode= 'development')

import logging
from logging.handlers import RotatingFileHandler
log_file = '/usr/share/nginx/poppet/logs/production.log'
file_handler = RotatingFileHandler(log_file,'a', 1 * 1024 * 1024, 10)
app.logger.setLevel(logging.DEBUG)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
app.logger.addHandler(file_handler)




#app.logger.error("--------------------------APP RESTART------------------------------------------------------------")


