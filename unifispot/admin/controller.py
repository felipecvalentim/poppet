
try:
    # Ugly hack to force SSLv3 and avoid
    # urllib2.URLError: <urlopen error [Errno 1] _ssl.c:504:
    # error:14077438:SSL routines:SSL23_GET_SERVER_HELLO:tlsv1 alert internal error>
    import _ssl
    _ssl.PROTOCOL_SSLv23 = _ssl.PROTOCOL_TLSv1
except:
    pass

try:
    # Updated for python certificate validation
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context
except:
    pass

import sys
PYTHON_VERSION = sys.version_info[0]

if PYTHON_VERSION == 2:
    import cookielib
    import urllib2
elif PYTHON_VERSION == 3:
    import http.cookiejar as cookielib
    import urllib3
    import ast

import json
import logging
from time import time,sleep
import urllib
import gzip
from StringIO import StringIO

log = logging.getLogger(__name__)


class APIError(Exception):
    pass


class Controller:

    """Interact with a UniFi controller.

    Uses the JSON interface on port 8443 (HTTPS) to communicate with a UniFi
    controller. Operations will raise unifi.controller.APIError on obvious
    problems (such as login failure), but many errors (such as disconnecting a
    nonexistant client) will go unreported.

    >>> from unifi.controller import Controller
    >>> c = Controller('192.168.1.99', 'admin', 'p4ssw0rd')
    >>> for ap in c.get_aps():
    ...     print 'AP named %s with MAC %s' % (ap['name'], ap['mac'])
    ...
    AP named Study with MAC dc:9f:db:1a:59:07
    AP named Living Room with MAC dc:9f:db:1a:59:08
    AP named Garage with MAC dc:9f:db:1a:59:0b

    """

    def __init__(self, host, username, password, port=8443, version='v2', site_id='default'):
        """Create a Controller object.

        Arguments:
            host     -- the address of the controller host; IP or name
            username -- the username to log in with
            password -- the password to log in with
            port     -- the port of the controller host
            version  -- the base version of the controller API [v2|v3|v4]
            site_id  -- the site ID to connect to (UniFi >= 3.x)

        """

        self.host = host
        self.port = port
        self.version = version
        self.username = username
        self.password = password
        self.site_id = site_id
        self.url = 'https://' + host + ':' + str(port) + '/'
        self.api_url = self.url + self._construct_api_path(version)

        log.debug('Controller for %s', self.url)

        cj = cookielib.CookieJar()
        if PYTHON_VERSION == 2:
            handler=urllib2.HTTPSHandler(debuglevel=0)
            self.opener = urllib2.build_opener(handler,urllib2.HTTPCookieProcessor(cj))
        elif PYTHON_VERSION == 3:
            self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

        self._login(version)

    def __del__(self):
        if self.opener != None:
            self._logout()

    def _jsondec(self, data):
        if PYTHON_VERSION == 3:
            data = data.decode()
        obj = json.loads(data)
        if 'meta' in obj:
            if obj['meta']['rc'] != 'ok':
                raise APIError(obj['meta']['msg'])
        if 'data' in obj:
            return obj['data']
        return obj

    def _read(self, url, params=None):
        if PYTHON_VERSION == 3:
            if params is not None:
                params = ast.literal_eval(params)
                #print (params)
                params = urllib.parse.urlencode(params)
                params = params.encode('utf-8')
                res = self.opener.open(url, params)
            else:

                res = self.opener.open(url)
        elif PYTHON_VERSION == 2:
            self.opener.addheaders = [('Accept-encoding', 'gzip,deflate')]
            process         = 1
            backofftime     = 1
            trial           = 1
            max_trials      = 5
            while ( process and trial < max_trials) :            
                try:                
                    res = self.opener.open(url, params) 
                except urllib2.URLError,e:
                    logger.info('URL error while trying connect to %s'%self.url)
                    sleep(backofftime)
                    backofftime = backofftime * 2
                    trial = trial + 1
                else:
                    process = 0                       
                    # if the response is gzip-encoded as expected
                    if res.info().get('Content-Encoding') == 'gzip':
                        # get ready for the content
                        content = ''            
                        # read the encoded response into a buffer
                        buffer = StringIO(res.read())
                        # gzip decode the response
                        f = gzip.GzipFile(fileobj=buffer)
                        # store the result
                        content = f.read()
                        # close the buffer
                        buffer.close()
                    else:
                        content = res.read()
                    return self._jsondec(content)

            return None
    def _construct_api_path(self, version,site_id=None):
        """Returns valid base API path based on version given

           The base API path for the URL is different depending on UniFi server version.
           Default returns correct path for latest known stable working versions.

        """
        if not site_id:
            site_id = self.site_id

        V2_PATH = 'api/'
        V3_PATH = 'api/s/' + site_id + '/'

        if(version == 'v2'):
            return V2_PATH
        if(version == 'v3'):
            return V3_PATH
        if(version == 'v4'):
            return V3_PATH
        else:
            return V2_PATH

    def _login(self, version):
        log.debug('login() as %s', self.username)
        
        if(version == 'v4'):
            params = "{'username':'" + self.username + "','password':'" + self.password + "'}"
            self.opener.open(self.url + 'api/login', params).read()
        else:
            if PYTHON_VERSION == 2:
                params = urllib.urlencode({'login': 'login',
                                   'username': self.username, 'password': self.password})
            elif PYTHON_VERSION == 3:
                params = urllib.parse.urlencode({'login': 'login',
                                   'username': self.username, 'password': self.password}).encode("UTF-8")
            process         = 1
            backofftime     = 1
            trial           = 1
            max_trials      = 5
            while ( process and trial < max_trials) :            
                try:                       
                    self.opener.open(self.url + 'login', params).read()
                except urllib2.URLError,e:
                    logger.info('URL error while trying connect to %s'%self.url)
                    sleep(backofftime)
                    backofftime = backofftime * 2
                    trial = trial + 1
                else:
                    process = 0                      

    def _logout(self):
        log.debug('logout()')
        process         = 1
        backofftime     = 1
        trial           = 1
        max_trials      = 5
        while ( process and trial < max_trials) :            
            try:         
                self.opener.open(self.url + 'logout').read()
            except urllib2.URLError,e:
                logger.info('URL error while trying connect to %s'%self.url)
                sleep(backofftime)
                backofftime = backofftime * 2
                trial = trial + 1
            else:
                process = 0                          

    def get_alerts(self):
        """Return a list of all Alerts."""

        return self._read(self.api_url + 'list/alarm')

    def get_alerts_unarchived(self):
        """Return a list of Alerts unarchived."""

        js = json.dumps({'_sort': '-time', 'archived': False})
        params = urllib.urlencode({'json': js})
        return self._read(self.api_url + 'list/alarm', params)

    def get_statistics_last_24h(self):
        """Returns statistical data of the last 24h"""

        return self.get_statistics_24h(time())

    def get_statistics_24h(self, endtime):
        """Return statistical data last 24h from time"""

        js = json.dumps(
            {'attrs': ["bytes", "num_sta", "time"], 'start': int(endtime - 86400) * 1000, 'end': int(endtime - 3600) * 1000})
        params = urllib.urlencode({'json': js})
        return self._read(self.api_url + 'stat/report/hourly.system', params)

    def get_events(self):
        """Return a list of all Events."""

        return self._read(self.api_url + 'stat/event')

    def get_sites(self):
        """Return a list of all sites, with significant information about each."""
        
        return self._read(self.url + 'api/self/sites')

    def get_aps(self,site_id=None):
        """Return a list of all AP:s, with significant information about each."""

        #Set test to 0 instead of NULL
        if not site_id:
            site_id = self.site_id
        api_url = self.url + self._construct_api_path(self.version,site_id=site_id)
        params = json.dumps({'_depth': 2, 'test': 0})
        return self._read(api_url + 'stat/device', params)

    def get_clients(self,site_id=None):
        """Return a list of all active clients, with significant information about each."""
        if not site_id:
            site_id = self.site_id
        api_url = self.url + self._construct_api_path(self.version,site_id=site_id)
        return self._read(api_url + 'stat/sta')

    def get_users(self):
        """Return a list of all known clients, with significant information about each."""

        return self._read(self.api_url + 'list/user')

    def get_user_groups(self):
        """Return a list of user groups with its rate limiting settings."""

        return self._read(self.api_url + 'list/usergroup')

    def get_wlan_conf(self):
        """Return a list of configured WLANs with their configuration parameters."""

        return self._read(self.api_url + 'list/wlanconf')

    def _run_command(self, command, params={}, mgr='stamgr',site_id =None):
        if not site_id:
            site_id = self.site_id
        api_url = self.url + self._construct_api_path(self.version,site_id=site_id)
        log.debug('_run_command(%s)', command)
        params.update({'cmd': command})
        if PYTHON_VERSION == 2:
            return self._read(api_url+ 'cmd/' + mgr, urllib.urlencode({'json': json.dumps(params)}))
        elif PYTHON_VERSION == 3:
            return self._read(api_url + 'cmd/' + mgr, urllib.parse.urlencode({'json': json.dumps(params)}))

    def _mac_cmd(self, target_mac, command, mgr='stamgr'):
        log.debug('_mac_cmd(%s, %s)', target_mac, command)
        params = {'mac': target_mac}
        self._run_command(command, params, mgr)

    def block_client(self, mac):
        """Add a client to the block list.

        Arguments:
            mac -- the MAC address of the client to block.

        """

        self._mac_cmd(mac, 'block-sta')

    def unblock_client(self, mac):
        """Remove a client from the block list.

        Arguments:
            mac -- the MAC address of the client to unblock.

        """

        self._mac_cmd(mac, 'unblock-sta')

    def disconnect_client(self, mac):
        """Disconnect a client.

        Disconnects a client, forcing them to reassociate. Useful when the
        connection is of bad quality to force a rescan.

        Arguments:
            mac -- the MAC address of the client to disconnect.

        """

        self._mac_cmd(mac, 'kick-sta')

    def restart_ap(self, mac):
        """Restart an access point (by MAC).

        Arguments:
            mac -- the MAC address of the AP to restart.

        """

        self._mac_cmd(mac, 'restart', 'devmgr')

    def restart_ap_name(self, name):
        """Restart an access point (by name).

        Arguments:
            name -- the name address of the AP to restart.

        """

        if not name:
            raise APIError('%s is not a valid name' % str(name))
        for ap in self.get_aps():
            if ap.get('state', 0) == 1 and ap.get('name', None) == name:
                self.restart_ap(ap['mac'])

    def archive_all_alerts(self):
        """Archive all Alerts
        """
        js = json.dumps({'cmd': 'archive-all-alarms'})
        params = urllib.urlencode({'json': js})
        answer = self._read(self.api_url + 'cmd/evtmgr', params)

    def create_backup(self):
        """Ask controller to create a backup archive file, response contains the path to the backup file.

        Warning: This process puts significant load on the controller may
                 render it partially unresponsive for other requests.
        """

        js = json.dumps({'cmd': 'backup'})
        params = urllib.urlencode({'json': js})
        answer = self._read(self.api_url + 'cmd/system', params)

        return answer[0].get('url')

    def get_backup(self, target_file='unifi-backup.unf'):
        """Get a backup archive from a controller.

        Arguments:
            target_file -- Filename or full path to download the backup archive to, should have .unf extension for restore.

        """
        download_path = self.create_backup()

        opener = self.opener.open(self.url + download_path)
        unifi_archive = opener.read()

        backupfile = open(target_file, 'w')
        backupfile.write(unifi_archive)
        backupfile.close()

    def authorize_guest(self, guest_mac, minutes, up_bandwidth=None, down_bandwidth=None, byte_quota=None, ap_mac=None):
        """
        Authorize a guest based on his MAC address.

        Arguments:
            guest_mac     -- the guest MAC address : aa:bb:cc:dd:ee:ff
            minutes       -- duration of the authorization in minutes
            up_bandwith   -- up speed allowed in kbps (optional)
            down_bandwith -- down speed allowed in kbps (optional)
            byte_quota    -- quantity of bytes allowed in MB (optional)
            ap_mac        -- access point MAC address (UniFi >= 3.x) (optional)
        """
        cmd = 'authorize-guest'
        js = {'mac': guest_mac, 'minutes': minutes}

        if up_bandwidth:
            js['up'] = up_bandwidth
        if down_bandwidth:
            js['down'] = down_bandwidth
        if byte_quota:
            js['bytes'] = byte_quota
        if ap_mac and self.version != 'v2':
            js['ap_mac'] = ap_mac

        return self._run_command(cmd, params=js)

    def unauthorize_guest(self, guest_mac):
        """
        Unauthorize a guest based on his MAC address.

        Arguments:
            guest_mac -- the guest MAC address : aa:bb:cc:dd:ee:ff
        """
        cmd = 'unauthorize-guest'
        js = {'mac': guest_mac}

        return self._run_command(cmd, params=js)

    def add_site(self, sitename):
        """Add a new site.

        Arguments:
            sitename -- namegiven for the new site.

        """
        log.debug('_sitemgr_cmd(%s, %s)', sitename, 'add-site')
        params = {'desc': sitename}
        return self._run_command('add-site', params, mgr='sitemgr')

    def adopt_ap(self, ap_mac):
        """Adopt a new AP.

        Arguments:
            ap_mac -- MAC address of the given ap.

        """
        log.debug('_devmgr_cmd(%s, %s)', ap_mac, "adopt")
        params = {'mac': ap_mac}
        return self._run_command('adopt', params, mgr='devmgr')    

    def check_ap_state(self,ap_mac):
        """Check the status of a given AP in the site
        Arguments:
            ap_mac -- MAC address of the given ap.

        """        
        return self._read(self.api_url + 'stat/device/%s'%ap_mac)

    def move_ap(self,ap_mac,site_id,site_code):
        """Move the specified AP from this site to another.

        Arguments:
            ap_mac -- MAC address of the given ap.
            site_id --  unifi site ID to which it should be moved
            site_code -- _id used by unifi for representing wifi site

        """
        log.debug('_sitemgr_cmd(%s, %s, %s)', ap_mac,site_id, "move-device")
        params = {'mac': ap_mac,'site':site_code}
        return self._run_command('move-device', params, mgr='sitemgr')  


    def forget_ap(self,ap_mac,site_id):
        """Forget the specified AP from controller

        Arguments:
            ap_mac -- MAC address of the given ap.
            site_id --  unifi site ID to which it should be moved
            site_code -- _id used by unifi for representing wifi site

        """
        log.debug('_sitemgr_cmd(%s, %s, %s)', ap_mac,site_id, "delete-device")
        params = {'mac': ap_mac}
        return self._run_command('delete-device', params, mgr='sitemgr',site_id=site_id)  



    def _set_setting(self,site_id, params={}, category='super_smtp'):

        api_url = self.url + self._construct_api_path(self.version,site_id=site_id)
        log.debug('_set_setting(%s)', category)
        if PYTHON_VERSION == 2:
            return self._read(api_url + 'set/setting/' + category, urllib.urlencode({'json': json.dumps(params)}))
        elif PYTHON_VERSION == 3:
            return self._read(api_url + 'set/setting/' + category, urllib.parse.urlencode({'json': json.dumps(params)}))        

    def set_smtp(self,site_id,host='127.0.0.1',port='25',use_ssl=False,
            use_auth=False,username=None,x_password=None,use_sender=False,sender=None):

        """Set SMTP seetings for this site

        Arguments:


        """
        log.debug('setting SMTP settings for site:%s',self.site_id )
        params = {'host': host,'port':port,'use_ssl':use_ssl,
                   'use_auth':use_auth,'username':username,'x_password':x_password,'use_sender':use_sender,'sender':sender}
        return self._set_setting(site_id=site_id,params=params, category='super_smtp')          

    def create_site_admin(self,site_id,name,email):
        """Create Admin for the particular site

        Arguments:
            name -- Admin User Name.
            email -- Email
            site_id --  unifi site ID to which it should be moved

        """
        log.debug('_sitemgr_cmd(%s, %s, %s)', name,site_id, "invite-admin")
        params = {'name': name,'email':email,'site':site_id}
        return self._run_command('invite-admin', params, mgr='sitemgr',site_id=site_id)  

    def set_guest_access(self,site_id,site_code,portal_ip,portal_subnet,portal_hostname):

        """Set SMTP seetings for this site

        Arguments:


        """
        log.debug('setting Guest settings for site:%s',site_id )

        params =  {"portal_enabled":True,"auth":"custom","x_password":"","expire":"480","redirect_enabled":False,"redirect_url":'',
        "custom_ip":portal_ip,"portal_customized":False,"portal_use_hostname":True,"portal_hostname":
        portal_hostname,"voucher_enabled":False,"payment_enabled":False,"gateway":"paypal","x_paypal_username":
        "","x_paypal_password":"","x_paypal_signature":"","paypal_use_sandbox":False,"x_stripe_api_key":"","x_quickpay_merchantid":
        "","x_quickpay_md5secret":"","x_authorize_loginid":"","x_authorize_transactionkey":"","authorize_use_sandbox":
        False,"x_merchantwarrior_merchantuuid":"","x_merchantwarrior_apikey":"","x_merchantwarrior_apipassphrase":
        "","merchantwarrior_use_sandbox":False,"x_ippay_terminalid":"","ippay_use_sandbox":False,"restricted_subnet_1":
        "192.168.0.0/16","restricted_subnet_2":"172.16.0.0/12","restricted_subnet_3":"10.0.0.0/8","allowed_subnet_1":
        portal_subnet,"key":"guest_access","site_id":site_code}  

        return self._set_setting(site_id=site_id,params=params, category='guest_access')  