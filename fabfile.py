from fabric.api import *


env.hosts = ['localhost']


def remote_uname():
    run('uname -a')

def remote_hostname():
    return run('hostname')

def apt_get(*packages):
    sudo('apt-get -y --no-upgrade install %s' % ' '.join(packages), shell=False)

def apt_get_update():
    sudo('apt-get update')


def install_nginx():
    with settings(hide('warnings', 'stderr'), warn_only=True):
        result = sudo('dpkg-query --show nginx')
    if result.failed is False:
        warn('nginx is already installed')
        return    
    apt_get('nginx')

def install_mysql_server():
    with settings(hide('warnings', 'stderr'), warn_only=True):
        result = sudo('dpkg-query --show mysql-server')
    if result.failed is False:
        warn('mysql-server is already installed')
        return    
    apt_get('mysql-server')    

def install_redis():
    with settings(hide('warnings', 'stderr'), warn_only=True):
        result = sudo('dpkg-query --show redis-server')
    if result.failed is False:
        warn('redis-server is already installed')
        return    
    apt_get('redis-server')

def install_supervisor():
    with settings(hide('warnings', 'stderr'), warn_only=True):
        result = sudo('dpkg-query --show supervisor')
    if result.failed is False:
        warn('supervisor is already installed')
        return    
    apt_get('supervisor')


def install_iptables_persistant():
    run('DEBIAN_FRONTEND=noninteractive apt-get install iptables-persistent --yes --force-yes')


def install_unifispot():
    run('apt-get install python-dev libmysqlclient-dev python-pip git bc nginx -y') 
    run('pip install -U pip')    
    with cd("/usr/share/nginx/"):
        run('mkdir -p unifispot/instance')
        run('touch unifispot/instance/__init__.py')
        run(' cp instance_sample.py /usr/share/nginx/unifispot/instance/config.py')
    with cd("/usr/share/nginx/unifispot"):
        run('mkdir -p unifispot/static/uploads/')
        run('pip install virtualenv')
        run('virtualenv .env')
        run('mkdir -p  logs')
        with prefix('source .env/bin/activate'):          
            run('pip install -r requirements.txt')        
    #configure uwsgi
    run('mkdir -p /var/log/uwsgi')
    run('chown -R www-data:www-data /var/log/uwsgi')   
    run('mkdir -p /etc/uwsgi && sudo mkdir -p /etc/uwsgi/vassals')
    run('rm -rf /etc/uwsgi/vassals/uwsgi.ini ')
    run('ln -s /usr/share/nginx/unifispot/uwsgi.ini /etc/uwsgi/vassals')
    run('chown -R www-data:www-data /usr/share/nginx/unifispot')
    run('chown -R www-data:www-data /var/log/uwsgi/')
    run('cp /usr/share/nginx/unifispot/uwsgi.conf /etc/init/')
    run('rm -rf /etc/nginx/sites-enabled/default')
    with cd('/etc/nginx/sites-available'):
        run('cp wifiapp.conf /etc/nginx/sites-available/wifiapp.conf')
        run('ln -s /etc/nginx/sites-available/wifiapp.conf /etc/nginx/sites-enabled/wifiapp')
        run('rm /etc/nginx/sites-enabled/default')

    run('service nginx restart')
    run('service uwsgi restart')



def configure_firewall_app(flush=True):
    internal_ips = droplets.get_all_private_ips()
    if flush:
        run('iptables -F')    
    run('iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT')
    run('iptables -A INPUT -p tcp --dport 22 -j ACCEPT')
    run('iptables -A INPUT -p tcp --dport 80 -j ACCEPT')
    run('iptables -A INPUT -p tcp --dport 443 -j ACCEPT')
    run('iptables -I INPUT 1 -i lo -j ACCEPT')
    run('iptables -A INPUT -p tcp --dport 8081 -j ACCEPT')
    run('iptables -A INPUT -p tcp --dport 8080 -j ACCEPT')
    run('iptables -A INPUT -p tcp --dport 8443 -j ACCEPT')
    run('iptables -A INPUT -p tcp --dport 8880 -j ACCEPT')
    run('iptables -A INPUT -p tcp --dport 8843 -j ACCEPT')
    run('iptables -A INPUT -p tcp --dport 27117 -j ACCEPT')  
    run('iptables -A INPUT -j DROP')
    run('invoke-rc.d iptables-persistent save')
 


def configure_celery():
    run('ln -s /usr/share/nginx/unifispot/supervisord.conf  /etc/supervisor/conf.d/unifispot_celery.conf')
    run('service supervisor restart')

def build_new_app_server():
    apt_get_update()
    install_nginx()
    install_supervisor()
    install_unifispot()
    configure_celery()
    install_iptables_persistant()
    configure_firewall_app()
