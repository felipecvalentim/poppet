

BUILDDIR=/usr/share/nginx/poppet
CONFFILE=/usr/share/nginx/poppet/instance/config.py

cd "$BUILDDIR"

if [ ! -d migrations ]; then
    .env/bin/python manage.py db init

fi

#Check if DB is properly configured
if  ! .env/bin/python manage.py db current >/dev/null 2>/dev/null  ; then  
    read -p "Please Enter your MySQL Host name [localhost]: " host
    host=${host:-localhost}
    read -p "Please Enter your MySQL Root Username [root]: " username
    username=${username:-root}
    read -s -p "Please Enter your MySQL Root Password []: " passwd
    echo " Trying to create a new Db named poppet"
    mysql -u $username -p$passwd -e "create database poppet";
    sed -i "s/^SQLALCHEMY_DATABASE_URI.*/SQLALCHEMY_DATABASE_URI=\"mysql:\/\/$username:$passwd@$host\/poppet\"/g"  $CONFFILE
fi

.env/bin/python manage.py db migrate
.env/bin/python manage.py db upgrade
.env/bin/python manage.py init_data

mkdir -p /etc/uwsgi
mkdir -p /etc/uwsgi/vassals
rm -rf /etc/uwsgi/vassals/uwsgi.ini
ln -s /usr/share/nginx/poppet/uwsgi.ini /etc/uwsgi/vassals/uwsgi.ini
chown -R www-data:www-data /usr/share/nginx/poppet
chown -R www-data:www-data /var/log/uwsgi/
cp uwsgi.conf /etc/init/
rm -rf /etc/nginx/sites-enabled/default
cp wifiapp.conf /etc/nginx/sites-available/wifiapp.conf
ln -s /etc/nginx/sites-available/wifiapp.conf /etc/nginx/sites-enabled/wifiapp
rm /etc/nginx/sites-enabled/default


