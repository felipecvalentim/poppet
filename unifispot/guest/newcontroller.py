
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


import cookielib
import urllib2
import requests
import os
import hashlib
import pickle
import requests_cache
import json
import logging
from time import time
import urllib


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

    def __init__(self, host, username, password, port=8443, version='v4', site_id='default'):
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
        #keep cookies in a file for later use
        url_hash = hashlib.md5(self.url).hexdigest()
        self.cookiefile = '/tmp/%s'%url_hash
        self.session = requests.Session()
        #automatic request retries http://www.mobify.com/blog/http-requests-are-hard/
        # `mount` a custom adapter that retries failed connections for HTTP and HTTPS requests.
        self.session.mount("http://", requests.adapters.HTTPAdapter(max_retries=4))
        self.session.mount("https://", requests.adapters.HTTPAdapter(max_retries=4))
        log.debug('Controller for %s', self.url)


    def save_cookies(self):
        with open(self.cookiefile, 'w') as f:
            f.truncate()
            pickle.dump(self.session.cookies._cookies, f)
            print self.session.cookies._cookies


    def load_cookies(self):
        if not os.path.isfile(self.cookiefile):
            return False

        with open(self.cookiefile) as f:
            cookies = pickle.load(f)
            if cookies:
                jar = requests.cookies.RequestsCookieJar()
                jar._cookies = cookies
                self.session.cookies = jar
                return True
            else:
                return False

    def _jsondec(self, data):
        obj = json.loads(data)
        print obj
        if 'meta' in obj:
            if obj['meta']['rc'] != 'ok':
                raise APIError(obj['meta']['msg'])
        if 'data' in obj:
            return obj['data']
        return obj

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

    def _read(self, url, params=None,cache=False):
        if not self.load_cookies() :           
            log.debug('No cookies found for controller %s going to try login'%self.url)
            self._login()

        r = self.session.post(url,json=params,verify=False)
        if r.status_code == 401: # maybe session expired
            log.debug('Looks like session expired for %s going to try login'%self.url)
            self._login()   
            r = self.session.post(url,json=params,verify=False)
            r.raise_for_status() 
        else:
            r.raise_for_status()   
        return self._jsondec(r.text)

    def _login(self):
        log.debug('login() as %s', self.username)
        params = "{'username':'" + self.username + "','password':'" + self.password + "'}"
        r = self.session.post(self.url + 'api/login',data=params,verify=False)
        r.raise_for_status()
        self.save_cookies()

    def get_events(self):
        """Return a list of all Events."""

        return self._read(self.api_url + 'stat/event')


    def _run_command(self, command, params={}, mgr='stamgr',site_id =None):
        if not site_id:
            site_id = self.site_id
        api_url = self.url + self._construct_api_path(self.version,site_id=site_id)
        log.debug('_run_command(%s)', command)
        params.update({'cmd': command})
        return self._read(api_url+ 'cmd/' + mgr, params)

    def authorize_guest(self, guest_mac, minutes=60, up_bandwidth=None, down_bandwidth=None, byte_quota=None, ap_mac=None):
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

        try:
            self._run_command(cmd, params=js)
        except:
            log.exception('Error while trying to authorize guest:%s for controller:%s'%(guest_mac,self.url))



