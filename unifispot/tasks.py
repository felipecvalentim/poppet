from unifispot import celery
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from celery.utils.log import get_task_logger
from flask import current_app
import time,arrow
from unifispot.base.utils.email import send_email
from unifispot.guest.models import Guest
from unifispot.client.models import Wifisite
from unifispot.extensions import db
from unifispot.exports.helper import get_api_endpoint
from unifispot.const import API_END_POINT_NONE





@celery.task(autoretry_on=Exception)
def celery_mail(*args, **kwargs):
    time.sleep(5)
    current_app.logger.error("hjahdjahdjhajdsha")


@periodic_task(run_every=(crontab(minute="*")))
def celery_mail1(*args, **kwargs):
    #send_email("TEST", body='jhsjdh', html='Minute', recipients=['rakesh@rakeshmukundan.in',], throttle=10)
    current_app.logger.error("Minute")


@periodic_task(run_every=(crontab(minute="*/5")))
def celery_mail2(*args, **kwargs):
    #send_email("TEST", body='jhsjdh', html='5 Minute', recipients=['rakesh@rakeshmukundan.in',], throttle=10)
    current_app.logger.error("5 Minute")

#task for handling API export after Guest has created
@celery.task(autoretry_on=Exception,max_retries=5)
def celery_export_api(guestid=None):
    guest = Guest.query.filter_by(id=guestid).first()
    if not guest:
        current_app.logger.error("Guest ID:%s is invalid"%guestid)
        return None
    wifisite = Wifisite.query.filter_by(id=guest.site_id).first()
    if not wifisite or wifisite.api_export == API_END_POINT_NONE :
        current_app.logger.error("Guest ID:%s has invalid site or API export is not configured"%guestid)   
        return None
    if guest.apisync==1:
        current_app.logger.error("Guest ID:%s has already synched"%guestid)   
        return None   
    if guest.demo==True:
        current_app.logger.debug("Guest ID:%s is a demo guest entry"%guestid)   
        return None              
    #get the endpoint and perform API export
    api_endpoint = get_api_endpoint(wifisite.api_export)
    current_app.logger.debug('Going to export guest ID:%s to API endpoint'%guest.id)
    if api_endpoint and api_endpoint(guest,wifisite):
        #API export was successful, mark entry as synched and put correct timestamp
        guest.apisync = True
        guest.synchedat = arrow.utcnow().datetime
        db.session.commit()

