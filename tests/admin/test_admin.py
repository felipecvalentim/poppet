''' Tests to check Admin  functions

'''

import sys

from flask import current_app
from sqlalchemy import and_,or_

from unifispot.guest.models import Guest,Device,Guestsession,Guesttrack
from unifispot.models import db
import time,uuid

from unifispot.const import *

def test_admin_dashboard(session):
    '''Testing admin dashboard 
    
    '''
    pass
