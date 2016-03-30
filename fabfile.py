from fabric.api import *


env.hosts = ['localhost']


def remote_uname():
    local('uname -a')

def remote_hostname():
    return local('hostname')

def apt_get(*packages):
    local('apt-get -y --no-upgrade install %s' % ' '.join(packages), shell=False)

def apt_get_update():
    local('apt-get update')


def install_nginx():
    with settings(hide('warnings', 'stderr'), warn_only=True):
        result = local('dpkg-query --show nginx')
    if result.failed is False:
        warn('nginx is already installed')
        return    
    apt_get('nginx')

def install_mysql_server():
    with settings(hide('warnings', 'stderr'), warn_only=True):
        result = local('dpkg-query --show mysql-server')
    if result.failed is False:
        warn('mysql-server is already installed')
        return    
    apt_get('mysql-server')    

def install_redis():
    with settings(hide('warnings', 'stderr'), warn_only=True):
        result = local('dpkg-query --show redis-server')
    if result.failed is False:
        warn('redis-server is already installed')
        return    
    apt_get('redis-server')

def install_supervisor():
    with settings(hide('warnings', 'stderr'), warn_only=True):
        result = local('dpkg-query --show supervisor')
    if result.failed is False:
        warn('supervisor is already installed')
        return    
    apt_get('supervisor')


def install_iptables_persistant():
    local('DEBIAN_FRONTEND=noninteractive apt-get install iptables-persistent --yes --force-yes')


def install_unifispot():
    local('apt-get install python-dev libmysqlclient-dev python-pip git bc nginx -y') 
    local('pip install -U pip')    
    with cd("/usr/share/nginx/"):
        local('git clone git@github.com:unifispot/poppet.git')
        local('mkdir -p puppet/instance')
        local('touch puppet/instance/__init__.py')
        local(' cp instance_sample.py /usr/share/nginx/puppet/instance/config.py')
    with cd("/usr/share/nginx/puppet"):
        local('mkdir -p unifispot/static/uploads/')
        local('pip install virtualenv')
        local('virtualenv .env')
        local('mkdir -p  logs')
        with prefix('source .env/bin/activate'):          
            local('pip install -r requirements.txt')        
    #configure uwsgi
    local('mkdir -p /var/log/uwsgi')
    local('chown -R www-data:www-data /var/log/uwsgi')   
    local('mkdir -p /etc/uwsgi && local mkdir -p /etc/uwsgi/vassals')
    local('rm -rf /etc/uwsgi/vassals/uwsgi.ini ')
    local('ln -s /usr/share/nginx/puppet/uwsgi.ini /etc/uwsgi/vassals')
    local('chown -R www-data:www-data /usr/share/nginx/puppet')
    local('chown -R www-data:www-data /var/log/uwsgi/')
    local('cp /usr/share/nginx/puppet/uwsgi.conf /etc/init/')
    local('rm -rf /etc/nginx/sites-enabled/default')
    with cd('/etc/nginx/sites-available'):
        local('cp wifiapp.conf /etc/nginx/sites-available/wifiapp.conf')
        local('ln -s /etc/nginx/sites-available/wifiapp.conf /etc/nginx/sites-enabled/wifiapp')
        local('rm /etc/nginx/sites-enabled/default')

    local('service nginx restart')
    local('service uwsgi restart')



def configure_firewall_app(flush=True):
    internal_ips = droplets.get_all_private_ips()
    if flush:
        local('iptables -F')    
    local('iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT')
    local('iptables -A INPUT -p tcp --dport 22 -j ACCEPT')
    local('iptables -A INPUT -p tcp --dport 80 -j ACCEPT')
    local('iptables -A INPUT -p tcp --dport 443 -j ACCEPT')
    local('iptables -I INPUT 1 -i lo -j ACCEPT')
    local('iptables -A INPUT -p tcp --dport 8081 -j ACCEPT')
    local('iptables -A INPUT -p tcp --dport 8080 -j ACCEPT')
    local('iptables -A INPUT -p tcp --dport 8443 -j ACCEPT')
    local('iptables -A INPUT -p tcp --dport 8880 -j ACCEPT')
    local('iptables -A INPUT -p tcp --dport 8843 -j ACCEPT')
    local('iptables -A INPUT -p tcp --dport 27117 -j ACCEPT')  
    local('iptables -A INPUT -j DROP')
    local('invoke-rc.d iptables-persistent save')
 


def configure_celery():
    local('ln -s /usr/share/nginx/unifispot/supervisord.conf  /etc/supervisor/conf.d/unifispot_celery.conf')
    local('service supervisor restart')

def build_new_app_server():
    apt_get_update()
    install_nginx()
    install_supervisor()
    install_unifispot()
    configure_celery()
    install_iptables_persistant()
    configure_firewall_app()
