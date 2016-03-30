from flask import Blueprint,render_template,jsonify,request,current_app,abort,redirect,url_for,flash
from functools import wraps
from sqlalchemy import and_,or_
import uuid
from functools import wraps
from facebook import get_user_from_cookie, GraphAPI
from .newcontroller import Controller
import datetime
import random
import arrow
from .models import Guest,Device,Guestsession,Guesttrack,Facebookauth,Smsdata
from .forms import FacebookTrackForm,generate_emailform,generate_voucherform,generate_smsform
from unifispot.client.models import Landingpage
from unifispot.const import *
from unifispot.extensions import db
from unifispot.base.utils.helper import format_url
from unifispot.base.utils.forms import print_errors,get_errors
from unifispot.admin.models import Admin
from unifispot.superadmin.models import Account
from unifispot.tasks import celery_export_api
from unifispot.client.models import Wifisite,Voucher

bp = Blueprint('guest', __name__,template_folder='templates')



@bp.route('/s/<site_id>/',methods = ['GET', 'POST'])
def guest_portal(site_id):

    #-----code to handle CNA requests
    #If CNA bypassing is needed (Social authentication/Advertisement options enabled)
    #check for User agent and return success page if its CNA request
    #add logging as well

    #--get all URL parameters, expected URL format--
    device_mac = request.args.get('id')
    ap_mac   = request.args.get('ap')   
    orig_url = request.args.get('url')   
    demo     = request.args.get('demo')
    utcnow   = arrow.utcnow().naive
  
    if not device_mac or not ap_mac:
        current_app.logger.error("Guest portal called with empty ap_mac/user_mac URL:%s"%request.url)
        abort(404)
    landing_site    = None
    landing_site    = Wifisite.query.filter_by(unifi_id=site_id).first()
    if not landing_site:
        current_app.logger.error("Guest portal called with unknown UnifiID URL:%s"%request.url)
        abort(404)       

    #apple CNA bypass
    if landing_site.fb_login_en():
        ua = request.headers.get('User-Agent')
        if ua and 'CaptiveNetworkSupport' in ua:
            current_app.logger.debug('Wifiguest Log - Site ID:%s apple CNA detected, serve success page Guest with MAC:%s just visited from AP:%s'%(landing_site.id,device_mac,ap_mac))
            return '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2//EN"><HTML><HEAD>
                        <TITLE>Success</TITLE></HEAD><BODY>Success</BODY></HTML>'''

    current_app.logger.debug('Wifiguest Log - Site ID:%s guest_portal Guest with MAC:%s just visited from AP:%s'%(landing_site.id,device_mac,ap_mac))
    ##-----------check for number of hits allowed per account TODO

    guest_device = None
    #create guest tracking entry
    track_id = str(uuid.uuid4())
    guest_track = Guesttrack(ap_mac=ap_mac,device_mac=device_mac,site=landing_site,state=GUESTRACK_INIT,orig_url=orig_url,track_id=track_id)
    if demo:
        guest_track.demo = 1
    db.session.add(guest_track)
    landing_site.guesttracks.append(guest_track)    

    #Initialize the session, check if the user has recently logged in 
    guest_session = Guestsession.query.filter( and_(Guestsession.mac==device_mac,Guestsession.site_id==landing_site.id,Guestsession.expiry > utcnow)).first() 

    #---------TODO add more session expiry checks



    #Check if the device was ever logged
    guest_device =  Device.query.filter(and_(Device.mac==device_mac,Device.site_id==landing_site.id)).first()
    if not guest_session:
        #create session
        guest_session = Guestsession(mac=device_mac,state=SESSION_INIT,site=landing_site)
        guest_session.expiry = arrow.utcnow().replace(minutes=60).naive
        print '------------%s'%guest_session.expiry
        if demo:
            guest_session.demo = 1
        db.session.add(guest_session)
        landing_site.sessions.append(guest_session)
        #check for guest device
        if guest_device:
            #device was logged once, add session to the device      
            guest_device.sessions.append(guest_session)

        else:
            #device was never logged, create a new device and add a session
            guest_device = Device(mac=device_mac,site=landing_site,state=DEVICE_INIT)
            landing_site.devices.append(guest_device)
            if demo:
                guest_session.demo = 1            
            db.session.add(guest_device)
            guest_device.sessions.append(guest_session)
        db.session.commit()
    #session exists
    else:
        #update last seen
        guest_session.lastseen = utcnow     
        if not guest_device:
            db.session.commit() 
            current_app.logger.error('Wifiguest Log - Site ID:%s guest_portal guest_session without guest_device MAC:%s just visited from AP:%s'%(landing_site.id,device_mac,ap_mac))
            abort(404)    
    #connect this session to our guest track entry
    guest_track.session = guest_session
    guest_session.guesttracks.append(guest_track)
    guest_track.state = GUESTRACK_SESSION
    db.session.commit()    
    ###---------------TODO ADD Date/Time Limiting Code here----------------------------------------
    

    ###----------------Code to show landing page------------------------------------------------------
    if landing_site.auth_method == AUTH_TYPE_EMAIL:
        #AUTH mode is set to email show the landing page with configured landing page
        return redirect(url_for('guest.email_login',track_id=guest_track.track_id),code=302)
        abort(404)   
    elif landing_site.auth_method == AUTH_TYPE_VOUCHER:
        #AUTH mode is set to voucher
        return redirect(url_for('guest.voucher_login',track_id=guest_track.track_id),code=302)  

    elif landing_site.auth_method == AUTH_TYPE_SOCIAL:
        #AUTH mode is set to voucher       
        return redirect(url_for('guest.social_login',track_id=guest_track.track_id),code=302)    

    elif landing_site.auth_method == AUTH_TYPE_SMS:
        #AUTH mode is set to voucher       
        return redirect(url_for('guest.sms_login',track_id=guest_track.track_id),code=302) 
               
    else:
        return get_landing_page(site_id=landing_site.id,landing_site=landing_site,track_id=guest_track.track_id)


@bp.route('/auth/guest/<track_id>')
def authorize_guest(track_id):
    '''Function called after respective auth mechanisms are completed
    
       This function send API commands to controller, redirect user to correct URL
    '''
    
    #
    #Validate track id and get all the needed variables
    guest_track = Guesttrack.query.filter_by(track_id=track_id).first()
    if not guest_track:
        current_app.logger.error("Called authorize_guest with wrong track ID:%s"%track_id)
        abort(404)
        
    #validate session associated with this track ID
    guest_session = Guestsession.query.filter_by(id=guest_track.session_id).first()
    if not guest_session:
        current_app.logger.error("Called authorize_guest with wrong Session from track ID:%s"%track_id)
        abort(404)   


    #Check if the session is authorized
    if not guest_session.state == SESSION_AUTHORIZED or guest_session.expiry < arrow.utcnow().naive:
        current_app.logger.error("Called authorize_guest with wrong Non Authorized session with track ID:%s"%track_id)
        abort(404) 

    current_app.logger.debug('Wifiguest Log - Site ID:%s authorize_guest with trackid :%s'%(guest_track.site_id,guest_track.id))
    #Send  unifi API commands if the user has completed login
    duration = guest_session.duration if guest_session.duration else 60
    if not current_app.config['NO_UNIFI'] :
        #code to send auth command to controller
        account = Account().query.filter_by(id=guest_session.site.account_id).first()
        settings = account.get_settings()
        try:
            c =  Controller(settings['unifi_server'], settings['unifi_user'], settings['unifi_pass'],'8443','v4',guest_track.site.unifi_id)       
            c.authorize_guest(guest_track.device_mac,duration,ap_mac=guest_track.ap_mac)    
        except:
            current_app.logger.exception('Wifiguest Log - Site ID:%s authorize_guest exception with trackid :%s'%(guest_track.site_id,guest_track.id))
            abort(500)
    #update session expiry to now + authorized time
    guest_session.expiry = arrow.utcnow().replace(minutes=duration + 10).naive
    db.session.commit()
    #Code to handle guest after successful login 
    
    #if guest_track.site.redirect_method == REDIRECT_ORIG_URL and guest_track.orig_url:
        #return redirect(format_url(guest_track.orig_url),code=302)
    #elif guest_track.site.redirect_url:
        #redirect User to default URL if configured
       # return redirect(format_url(guest_track.site.redirect_url),code=302)
    #else:
        #redirect user to google.com
    return redirect(format_url("www.google.com"),code=302)

@bp.route('/tempauth/guest/<track_id>')
def temp_authorize_guest(track_id):
    '''Function for giving temporary internet access for a client
    
       This function send API commands to controller, return ok
    '''
    guest_track = Guesttrack.query.filter_by(track_id=track_id).first()
    if not guest_track :
        current_app.logger.error("Called temp_authorize_guest with wrong track ID:%s"%track_id)
        return jsonify({'status':0,'msg': "Error"})
        
    #validate session associated with this track ID
    guest_session = Guestsession.query.filter_by(id=guest_track.session_id).first()
    if not guest_session or guest_session.state != SESSION_TEMP_AUTH:
        current_app.logger.error("Called temp_authorize_guest with wrong Session from track ID:%s"%track_id)
        return jsonify({'status':0,'msg': "Error"})  

    current_app.logger.debug('Wifiguest Log - Site ID:%s temp_authorize_guest for track ID:%s'%(guest_track.site_id,guest_track.id))
    #prevent misuse
    if guest_session.temp_login >= 10 and guest_session.demo != 1 : 
        current_app.logger.info('Wifiguest Log - Site ID:%s temp_authorize_guest max tries reached for track ID:%s'%(guest_track.site_id,guest_track.id))
        return jsonify({'status':0,'msg': "You have already used up temporary logins for today"})
    else:
        guest_session.temp_login += 1
        db.session.commit()
    #get details from track ID and authorize
    if not current_app.config['NO_UNIFI'] :
        account = Account().query.filter_by(id=guest_session.site.account_id).first()
        settings = account.get_settings()   

        try:
            c =  Controller(settings['unifi_server'], settings['unifi_user'], settings['unifi_pass'],'8443','v4',guest_track.site.unifi_id)  
            c.authorize_guest(guest_track.device_mac,5,ap_mac=guest_track.ap_mac)    
        except:
            current_app.logger.exception('Exception occured while trying to authorize User')
            return jsonify({'status':0,'msg': "Error!!"})
        return jsonify({'status':1,'msg': "DONE"})
    else:
        return jsonify({'status':1,'msg': "DEBUG enabled"})

@bp.route('/social/guest/<track_id>',methods = ['GET', 'POST'])
def social_login(track_id):
    ''' Function to called if the site is configured with Social login    
    
    '''
    #
    #Validate track id and get all the needed variables
    guest_track = Guesttrack.query.filter_by(track_id=track_id).first()
    if not guest_track:
        current_app.logger.error("Called social_login with wrong track ID:%s"%track_id)
        abort(404)
        
    #validate session associated with this track ID
    guest_session   = Guestsession.query.filter_by(id=guest_track.session_id).first()
    if not guest_session:
        current_app.logger.error("Called social_login with wrong Session from track ID:%s"%track_id)
        abort(404)         
    guest_device    = Device.query.filter_by(id=guest_session.device_id).first()
    landing_site    = Wifisite.query.filter_by(id=guest_session.site_id).first()    
    if not guest_device or not landing_site:
        current_app.logger.error("Called social_login with wrong Device/Wifisite from track ID:%s"%track_id)
        abort(404) 
    #
    current_app.logger.debug('Wifiguest Log - Site ID:%s social_login for track ID:%s'%(guest_track.site_id,guest_track.id))
    #Check if the device already has a valid auth
    if  guest_device.state == DEVICE_AUTH  and guest_device.demo == 0:
        #Device has a guest element and is authorized
        guest_session.state = SESSION_AUTHORIZED
        guest_track.state   = GUESTRACK_SOCIAL_PREAUTH
        db.session.commit()
        #redirect to authorize_guest
        return redirect(url_for('guest.authorize_guest',track_id=guest_track.track_id),code=302)
    else:
        #show the configured landing page
        guest_session.state = SESSION_TEMP_AUTH
        db.session.commit()       
        if landing_site.fb_appid:
            fb_appid= landing_site.fb_appid
        else:
            fb_appid = current_app.config['FB_APP_ID']
        landing_page = Landingpage.query.filter_by(id=landing_site.default_landing).first()
        return render_template('guest/%s/social_landing.html'%landing_site.template,landing_site=landing_site,landing_page=landing_page,app_id=fb_appid,track_id=track_id)   
        
@bp.route('/facebook/check/<track_id>',methods = ['GET', 'POST'])
def facebook_login(track_id):
    ''' Function to called if the site is configured for advanced facebook authentication.
    
    '''
    #fbtrackform = FacebookTrackForm()
    auth_like = None
    auth_post = None
    #if fbtrackform.validate_on_submit():
    if request.method == 'POST':
        auth_like = request.form['authlike']
        auth_post = request.form['authpost']
    #Validate track id and get all the needed variables
    guest_track = Guesttrack.query.filter_by(track_id=track_id).first()
    if not guest_track:
        current_app.logger.error("Called authorize_guest with wrong track ID:%s"%track_id)
        abort(404)
        
    #validate session associated with this track ID
    guest_session   = Guestsession.query.filter_by(id=guest_track.session_id).first()
    if not guest_session:
        current_app.logger.error("Called authorize_guest with wrong Session from track ID:%s"%track_id)
        abort(404)         
    guest_device    = Device.query.filter_by(id=guest_session.device_id).first()
    landing_site    = Wifisite.query.filter_by(id=guest_session.site_id).first()    
    if  not guest_device or not landing_site:
        current_app.logger.error("Called authorize_guest with wrong Session/Device/Wifisite from track ID:%s"%track_id)
        abort(404) 

    # Attempt to get the short term access token for the current user.
    current_app.logger.debug('Wifiguest Log - Site ID:%s facebook_login for track ID:%s'%(guest_track.site_id,guest_track.id))
    if  auth_like != '1': #ensure this is first time visit, not the visit after like/post
        fb_appid= landing_site.fb_appid or current_app.config['FB_APP_ID']   
        fb_app_secret = landing_site.fb_app_secret or current_app.config['FB_APP_SECRET']
        check_user_auth = get_user_from_cookie(cookies=request.cookies, app_id=fb_appid,app_secret=fb_app_secret)      
        if not check_user_auth or not check_user_auth['uid']:
            #
            #User is not logged into DB app, redirect to social login page
            current_app.logger.debug('Wifiguest Log - Site ID:%s facebook_login  Used not logged in, redirecting to social_login for track ID:%s'%(guest_track.site_id,guest_track.id))
            return redirect(url_for('guest.social_login',track_id=track_id),code=302)

        #check this FB profile already added into our DB,else add it
        profile_check = Facebookauth.query.filter(and_(Facebookauth.profile_id==check_user_auth['uid'],Facebookauth.site_id==landing_site.id)).first()
        if not profile_check:

            profile_check = Facebookauth()
            profile_check.profile_id    = check_user_auth['uid']
            profile_check.token         = check_user_auth['access_token']
            profile_check.site = landing_site
            db.session.add(profile_check)
            db.session.commit
            current_app.logger.debug('Wifiguest Log - Site ID:%s facebook_login  adding new FB profile ID:%s for track ID:%s'%(guest_track.site_id,profile_check.id,guest_track.id))
            
        #profile already added to DB, check if the user had already authorized the site
        guest_check = Guest.query.filter(and_(Guest.site_id==guest_session.site_id,Guest.fb_profile==profile_check.id)).first()
        if not guest_check:
            #Guest entry for this user is not available in DB,add the same.
            try:
                graph = GraphAPI(check_user_auth['access_token'])
                profile = graph.get_object(profile_check.profile_id +'?locale=en_US&fields=name,email,first_name,last_name')
            except:
                #Exception while calling graph API, redirect user to same page to try again
                current_app.logger.exception('Wifiguest Log - Site ID:%s facebook_login  exception while API FB profile ID:%s for track ID:%s'%(guest_track.site_id,guest_track.id,profile_check.id))
                return redirect(url_for('guest.facebook_login',track_id=track_id),code=302)
            else:
                guest_check = Guest()
                guest_check.firstname    = profile.get('first_name')
                guest_check.lastname    = profile.get('last_name')
                guest_check.email   = profile.get('email')
                guest_check.site_id = guest_session.site_id
                guest_check.facebookauth = profile_check           
                profile_check.guests.append(guest_check)
                db.session.add(guest_check)
                db.session.commit()
                #New guest added create task for API export
                celery_export_api.delay(guest_check.id)     
                current_app.logger.debug('Wifiguest Log - Site ID:%s facebook_login  adding new Guest:%s for track ID:%s'%(guest_track.site_id,guest_check.id,guest_track.id))       
        #
        #even if guest entry was already added, assign the guest to device
        guest_device.guest  = guest_check
        guest_check.devices.append(guest_device)
        db.session.commit()
    else:
        guest_check = Guest.query.filter_by(id=guest_device.guest_id).first()
        if not guest_check:
            #
            #User is not logged into DB app, redirect to social login page
            current_app.logger.debug('Wifiguest Log - Site ID:%s facebook_login  Used not logged in after like/post, redirecting to social_login for track ID:%s'%(guest_track.site_id,guest_track.id))
            return redirect(url_for('guest.social_login',track_id=track_id),code=302)            

    if landing_site.auth_fb_like == 1:
        if guest_track.fb_liked !=1:
            if guest_check.fb_liked:
                # if the guest has liked the page already, mark guesttrack as liked
                current_app.logger.debug('Wifiguest Log - Site ID:%s facebook_login  guest already liked for track ID:%s'%(guest_track.site_id,guest_track.id))              
                guest_track.fb_liked = 1
                db.session.commit()
            elif auth_like == '1' :
                #quick hack to test for liking and posting, guest has skipped the liking, allow
                #internet for now and ask next time
                current_app.logger.debug('Wifiguest Log - Site ID:%s facebook_login  guest decided to skip  like for track ID:%s'%(guest_track.site_id,guest_track.id))
                guest_track.fb_liked = 1
                db.session.commit()
            elif auth_like == '2':
                #user has liked the page mark track and guest as liked               
                current_app.logger.debug('Wifiguest Log - Site ID:%s facebook_login  guest liked now for track ID:%s'%(guest_track.site_id,guest_track.id))
                guest_track.fb_liked = 1
                guest_check.fb_liked = 1
                db.session.commit()
            else:
                # show page asking user to like
                current_app.logger.debug('Wifiguest Log - Site ID:%s facebook_login  new guest show page to like for track ID:%s'%(guest_track.site_id,guest_track.id))
                landing_page = Landingpage.query.filter_by(id=landing_site.default_landing).first()
                fb_page = landing_site.fb_page or current_app.config['FB_PAGE_URL']
                return render_template("guest/%s/fb_like.html"%landing_site.template,landing_page = landing_page,font_list=font_list,app_id=fb_appid,track_id=track_id,fb_page=fb_page)


    #mark sessions as authorized
    guest_session.state = SESSION_AUTHORIZED
    guest_track.state   = GUESTRACK_NEW_AUTH
    if guest_check.fb_liked == 1 : # if guest has full filled all the social login criterias,mark the device as authed
        guest_device.state  = DEVICE_AUTH
    db.session.commit()
    return redirect(url_for('guest.authorize_guest',track_id=guest_track.track_id),code=302)
    

@bp.route('/email/guest/<track_id>',methods = ['GET', 'POST'])
def email_login(track_id):
    ''' Function to called if the site is configured with Social login    
    
    '''
    #
    #Validate track id and get all the needed variables
    guest_track = Guesttrack.query.filter_by(track_id=track_id).first()
    if not guest_track:
        current_app.logger.error("Called email_login with wrong track ID:%s"%track_id)
        abort(404)
        
    #validate session associated with this track ID
    guest_session   = Guestsession.query.filter_by(id=guest_track.session_id).first()
    if not guest_session:
        current_app.logger.error("Called email_login with wrong Session from track ID:%s"%track_id)
        abort(404)   

    guest_device    = Device.query.filter_by(id=guest_session.device_id).first()
    landing_site    = Wifisite.query.filter_by(id=guest_session.site_id).first()    
    if  not guest_device or not landing_site:
        current_app.logger.error("Called email_login with wrong Session/Device/Wifisite from track ID:%s"%track_id)
        abort(404) 
    current_app.logger.debug('Wifiguest Log - Site ID:%s email_login for track ID:%s'%(guest_track.site_id,guest_track.id))
    #
    #Check if the device already has a valid auth
    if  guest_device.state == DEVICE_AUTH and guest_device.demo == 0:
        #Device has a guest element and is authorized
        guest_session.state = SESSION_AUTHORIZED
        guest_track.state   = GUESTRACK_SOCIAL_PREAUTH
        guest_device.state  = DEVICE_AUTH
        db.session.commit()
        #redirect to authorize_guest
        return redirect(url_for('guest.authorize_guest',track_id=guest_track.track_id),code=302)
    else:
        #show the configured landing page
        email_form = generate_emailform(landing_site.emailformfields)

        if email_form.validate_on_submit():
            newguest = Guest()
            newguest.populate_from_email_form(email_form,landing_site.emailformfields)
            newguest.site = landing_site
            db.session.add(newguest)
            db.session.commit()
            #New guest added create task for API export
            celery_export_api.delay(newguest.id)
            #mark sessions as authorized
            guest_session.state = SESSION_AUTHORIZED
            guest_track.state   = GUESTRACK_NEW_AUTH
            guest_device.guest  = newguest
            newguest.demo       = guest_session.demo
            newguest.devices.append(guest_device)
            guest_device.state  = DEVICE_AUTH
            db.session.commit()
            current_app.logger.debug('Wifiguest Log - Site ID:%s email_login  new guest track ID:%s'%(guest_track.site_id,guest_track.id))
            return redirect(url_for('guest.authorize_guest',track_id=guest_track.track_id),code=302)
        landing_page = Landingpage.query.filter_by(id=landing_site.default_landing).first()
        return render_template('guest/%s/email_landing.html'%landing_site.template,landing_site=landing_site,landing_page=landing_page,email_form=email_form)   
        

@bp.route('/voucher/guest/<track_id>',methods = ['GET', 'POST'])
def voucher_login(track_id):
    ''' Function to called if the site is configured with Voucher login    
    
    '''
    #
    #Validate track id and get all the needed variables
    guest_track = Guesttrack.query.filter_by(track_id=track_id).first()
    if not guest_track:
        current_app.logger.error("Called email_login with wrong track ID:%s"%track_id)
        abort(404)
        
    #validate session associated with this track ID
    guest_session   = Guestsession.query.filter_by(id=guest_track.session_id).first()
    if not guest_session:
        current_app.logger.error("Called email_login with wrong Session from track ID:%s"%track_id)
        abort(404)   

    guest_device    = Device.query.filter_by(id=guest_session.device_id).first()
    landing_site    = Wifisite.query.filter_by(id=guest_session.site_id).first()    
    if  not guest_device or not landing_site:
        current_app.logger.error("Called email_login with wrong Session/Device/Wifisite from track ID:%s"%track_id)
        abort(404) 
    current_app.logger.debug('Wifiguest Log - Site ID:%s voucher_login  for track ID:%s'%(guest_track.site_id,guest_track.id))
    #
    #Check if the device already has a valid auth
    if  guest_device.state == DEVICE_VOUCHER_AUTH and guest_device.demo == False:
        #Device has a guest element and is authorized before
        #check if the voucher is valid still
        expiry = arrow.get(guest_device.expires_at).timestamp
        time_now = arrow.utcnow().timestamp
        available_time = expiry - time_now
        if available_time > 60 : #atleast one minute is available
            #check if atleast one hour of time remaining in the voucher, else modify the session duration
            if available_time < 3600: 
                guest_session.duration = (available_time/60)
            guest_session.state = SESSION_AUTHORIZED
            guest_track.state   = GUESTRACK_VOUCHER_AUTH
            db.session.commit()
            #redirect to authorize_guest
            current_app.logger.debug('Wifiguest Log - Site ID:%s voucher_login already authenticated voucher for track ID:%s'%(guest_track.site_id,guest_track.id))
            return redirect(url_for('guest.authorize_guest',track_id=guest_track.track_id),code=302)
            
    voucher_form = generate_voucherform(landing_site.emailformfields)
    if voucher_form.validate_on_submit():
        #validate voucher
        voucher = Voucher.query.filter(and_(Voucher.site_id== landing_site.id,Voucher.voucher==voucher_form.voucher.data,Voucher.used==False)).first()
        if voucher:
            #valid voucher available
            newguest = Guest()
            newguest.populate_from_email_form(voucher_form,landing_site.emailformfields)
            newguest.site = landing_site
            db.session.add(newguest)
            db.session.commit()
            #New guest added create task for API export
            celery_export_api.delay(newguest.id)            
            #mark sessions as authorized
            guest_session.state = SESSION_AUTHORIZED
            guest_track.state   = GUESTRACK_VOUCHER_AUTH
            guest_device.guest  = newguest
            newguest.demo        = guest_session.demo
            newguest.devices.append(guest_device)
            #update device with voucher expirty time
            expiry = arrow.get(arrow.utcnow().timestamp + voucher.duration_t)
            guest_device.expires_at = expiry.datetime
            voucher.device_id = guest_device.id
            voucher.used = True
            voucher.used_at = arrow.utcnow().datetime
            guest_device.state  = DEVICE_VOUCHER_AUTH
            db.session.commit()
            current_app.logger.debug('Wifiguest Log - Site ID:%s voucher_login new guest:%s for track ID:%s'%(guest_track.site_id,newguest.id,guest_track.id))
            return redirect(url_for('guest.authorize_guest',track_id=guest_track.track_id),code=302)
        else:           
            current_app.logger.debug('Wifiguest Log - Site ID:%s voucher_login  in valid vouher value:%s for track ID:%s'%(guest_track.site_id,voucher_form.voucher.data,guest_track.id))
            flash(u'Invalid Voucher ID', 'danger')
       
    
    landing_page = Landingpage.query.filter_by(id=landing_site.default_landing).first()
    return render_template('guest/%s/voucher_landing.html'%landing_site.template,landing_site=landing_site,landing_page=landing_page,voucher_form=voucher_form)   
    

@bp.route('/sms/guest/<track_id>',methods = ['GET', 'POST'])
def sms_login(track_id):
    ''' Function to called if the site is configured with SMS login    
    
    '''
    #
    #Validate track id and get all the needed variables
    guest_track = Guesttrack.query.filter_by(track_id=track_id).first()
    if not guest_track:
        current_app.logger.error("Called email_login with wrong track ID:%s"%track_id)
        abort(404)
        
    #validate session associated with this track ID
    guest_session   = Guestsession.query.filter_by(id=guest_track.session_id).first()
    if not guest_session:
        current_app.logger.error("Called email_login with wrong Session from track ID:%s"%track_id)
        abort(404)   

    guest_device    = Device.query.filter_by(id=guest_session.device_id).first()
    landing_site    = Wifisite.query.filter_by(id=guest_session.site_id).first()    
    if  not guest_device or not landing_site:
        current_app.logger.error("Called email_login with wrong Session/Device/Wifisite from track ID:%s"%track_id)
        abort(404) 
    #
    #
    current_app.logger.debug('Wifiguest Log - Site ID:%s sms_login for track ID:%s'%(guest_track.site_id,guest_track.id))
    sms_form = generate_smsform(landing_site.emailformfields)
    if sms_form.validate_on_submit():
        #check if number validation is needed
        #TO DO
        #check_auth = Smsdata.query.filter_by(site_id=landing_site.id,phonenumber=sms_form.phonenumber.data,authcode=sms_form.authcode.data).first()
        #if check_auth and check_auth.status != SMS_CODE_USED :
        guest_check = Guest()
        guest_check.populate_from_email_form(sms_form,landing_site.emailformfields)
        guest_check.site_id    = guest_session.site_id
        guest_check.demo        = guest_session.demo
        db.session.add(guest_check)
        #New guest added create task for API export
        celery_export_api.delay(guest_check.id)            
        #mark sessions as authorized
        guest_session.state = SESSION_AUTHORIZED
        guest_track.state   = GUESTRACK_NEW_AUTH
        guest_device.state  = DEVICE_SMS_AUTH
        guest_device.guest  = guest_check
        guest_check.devices.append(guest_device)
        #check_auth.status = SMS_CODE_USED
        db.session.commit()
        current_app.logger.debug('Wifiguest Log - Site ID:%s sms_login new guest ID :%s for track ID:%s'%(guest_track.site_id,guest_check.id,guest_track.id))
        return redirect(url_for('guest.authorize_guest',track_id=guest_track.track_id),code=302)       
    #else:
        #print_errors(form)            
    
    landing_page = Landingpage.query.filter_by(id=landing_site.default_landing).first()
    return render_template('guest/%s/sms_landing.html'%landing_site.template,landing_site=landing_site,landing_page=landing_page,sms_form=sms_form)



@bp.route('/sms/send/<track_id>',methods = [ 'POST'])
def sms_send(track_id):
    ''' Function to called for sending sms auth code  
    
    '''
    phonenumber = request.form['phonenumber']

    if not phonenumber:
        return jsonify({'status':0,'msg':"Please Provide a Valid Mobile Number"})   
    #Validate track id and get all the needed variables
    guest_track = Guesttrack.query.filter_by(track_id=track_id).first()
    if not guest_track:
        current_app.logger.error("Called email_login with wrong track ID:%s"%track_id)
        abort(404)
        
    #validate session associated with this track ID
    guest_session   = Guestsession.query.filter_by(id=guest_track.session_id).first()
    if not guest_session:
        current_app.logger.error("Called email_login with wrong Session from track ID:%s"%track_id)
        abort(404)   

    guest_device    = Device.query.filter_by(id=guest_session.device_id).first()
    landing_site    = Wifisite.query.filter_by(id=guest_session.site_id).first()    
    if  not guest_device or not landing_site:
        current_app.logger.error("Called email_login with wrong Session/Device/Wifisite from track ID:%s"%track_id)
        abort(404) 
    #
    smsdata  = Smsdata.query.filter_by(device_id=guest_device.id,phonenumber=phonenumber).first()
    if not smsdata:
        smsdata = Smsdata(phonenumber=phonenumber,device=guest_device)
        db.session.add(smsdata)  
        db.session.commit()
    #
    time_now  = datetime.datetime.utcnow() 
    time_diff = time_now - smsdata.timestamp
    #check if the mobile number was already used
    #also check how many times the user has asked for SMS
    if smsdata.status == SMS_CODE_USED: #This number was used already once
        return jsonify({'status':0,'msg':"Wifi Package on mobile number has expired"})
    elif smsdata.status == SMS_DATA_NEW:
        #generate code 
        smsdata.authcode = random.randrange(10000,99999,1)
    elif smsdata.status == SMS_CODE_SEND:
        if smsdata.send_try > 5 and  (time_diff.total_seconds() < 15*60 ):
            wait_time = (15*60 - time_diff.total_seconds() )%60
            return jsonify({'status':0,'msg':"Looks like SMS network is having issues,please wait for %s minutes"%wait_time})
        elif smsdata.send_try !=0 and time_diff.total_seconds() < 30:
            return jsonify({'status':0,'msg':"Wait for atleast 30sec before trying again"})
    smsdata.timestamp = time_now
    smsdata.status = SMS_CODE_SEND
    smsdata.send_try = smsdata.send_try + 1
    db.session.commit()
    msg = "Activation code for Hotspot is:%s"%smsdata.authcode
    print msg
    return jsonify({'status':1,'msg':"Code has been send to the mobile"})
    

def get_landing_page(site_id,landing_page=None,landing_site=None,**kwargs):

    ''' Function to return configured landing page for a particular site    
    
    '''
    try:
        if not landing_site:
            landing_site = Wifisite.query.filter_by(id=site_id).first()
            current_app.logger.debug("SITE ID:%s"%landing_site.default_landing)
        if not landing_page:
            landing_page = Landingpage.query.filter_by(id=landing_site.default_landing).first()
    except:
        current_app.logger.exception("Exception while getting landing page/site for siteid:%s"%site_id)

    if not landing_site or not landing_page :
        #Given invalid site_id
        current_app.logger.info("Unknown landing_site or page specified n URL:%s"%request.url)
        abort(404)
    if landing_site.auth_method == AUTH_TYPE_SOCIAL:
        return render_template('guest/%s/social_landing.html'%landing_site.template,landing_site=landing_site,landing_page=landing_page,**kwargs)
    elif landing_site.auth_method == AUTH_TYPE_EMAIL:
        return render_template('guest/%s/email_landing.html'%landing_site.template,landing_site=landing_site,landing_page=landing_page,**kwargs)   
    elif landing_site.auth_method == AUTH_TYPE_VOUCHER:
        return render_template('guest/%s/voucher_landing.html'%landing_site.template,landing_site=landing_site,landing_page=landing_page,**kwargs)          

    elif landing_site.auth_method == AUTH_TYPE_SMS:
        return render_template('guest/%s/sms_landing.html'%landing_site.template,landing_site=landing_site,landing_page=landing_page,**kwargs)          
    else:
        return render_template('guest/%s/multi_landing.html'%landing_site.template,landing_site=landing_site,landing_page=landing_page,**kwargs)          
       