#! flask/bin/python
from os.path import abspath

from flask import current_app
from flask.ext.script import Manager
from flask.ext.assets import ManageAssets
from flask.ext.migrate import Migrate, MigrateCommand

from unifispot import create_app
from unifispot.extensions import db,mail,celery,redis


app = create_app(mode= 'development')

app.run(host='0.0.0.0',debug = True)


