import os
import pytest

from flask.ext.migrate import Migrate,upgrade,migrate,init,downgrade

from unifispot import create_app
from unifispot.models import db as _db
from unifispot.models import user_datastore
from flask.ext.security.utils import encrypt_password
from selenium import webdriver

import os
import shutil

from tests.data.data import init_data

#---------------enable logging while tests running-----------
import logging
from logging.handlers import RotatingFileHandler
logfile = 'alltests.log'
os.remove(logfile) if os.path.exists(logfile) else None
file_handler = RotatingFileHandler(logfile, 'a', 1 * 1024 * 1024, 10)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
##------------End logging Initilization-----------------------

@pytest.fixture(scope='session')
def app(request):
    """Session-wide test `Flask` application."""

    app = create_app(mode="e2e_testing")

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()
    
    ##------------More logging configuration---------------------
    app.logger.setLevel(logging.DEBUG)
    file_handler.setLevel(logging.DEBUG)
    app.logger.addHandler(file_handler)
    app.logger.info('--------------Starting Tests-----------------')
    ##------------More logging configuration END------------------
    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app

@pytest.fixture(scope='session')
def db(app, request):
    """Session-wide test database."""

    def teardown():
         _db.drop_all()
    _db.app = app
    _db.create_all()

    request.addfinalizer(teardown)
    return _db


@pytest.fixture(scope='session')
def session(db, request):
    """Creates a new database session for a test."""
    #connection = db.engine.connect()
    #transaction = connection.begin()

    #options = dict(bind=connection, binds={})
    #session = db.create_session(options=options)
    
    #db.session = session
    init_data(db.session)
    def teardown():
        #transaction.rollback()
        #connection.close()
        #session.remove()
        pass

    request.addfinalizer(teardown)
    return db.session

@pytest.fixture(scope='function')
def browser(request):
    driver = webdriver.Chrome('/home/user/Downloads/chromedriver/chromedriver')
    def teardown():
        driver.quit()
    request.addfinalizer(teardown)
    return driver