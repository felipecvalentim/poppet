BUILDDIR=/tmp/poppet_build
PKGDIR=/tmp/poppet_build/pkg

if [ -d "$BUILDDIR" ]; then
    printf '%s\n' "Removing Build DIrectory ($BUILDDIR)"
    rm -rf "$BUILDDIR"
fi
mkdir "$BUILDDIR"
mkdir "$PKGDIR"
cd "$BUILDDIR"

echo "------------------------------Getting latest Source files----------------------------"
#git clone https://github.com/unifispot/poppet.git
cp -r /home/user/projects/poppet/  $BUILDDIR

echo "------------------------------Create new venv and activate----------------------------"
cd poppet
virtualenv .env
source .env/bin/activate

echo "------------------------------Install all dependencies----------------------------"
pip install -r requirements.txt
mkdir instance
mkdir logs
mkdir touch instance/__init__.py
cp instance_sample.py instance/config.py
mkdir -p unifispot/static/uploads/

cd "$BUILDDIR"

echo "-----------------------------Building Packages-----------------------------"
fpm -s dir -t deb -n poppet -v 0.1 -d "nginx,redis-server,mysql-server,mysql-client,python-dev,libmysqlclient-dev,python-pip,git,bc"  --after-install poppet/scripts/post_install.sh  poppet/=/usr/share/nginx/poppet 
