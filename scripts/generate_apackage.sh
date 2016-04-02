BUILDDIR=/tmp/poppet_build
PKGDIR=/tmp/poppet_build/pkg

if [ -d "$BUILDDIR" ]; then
    printf '%s\n' "Removing Build DIrectory ($DIR)"
    rm -rf "$BUILDDIR"
fi
mkdir "$BUILDDIR"
mkdir "$PKGDIR"
cd "$BUILDDIR"
git clone https://github.com/unifispot/poppet.git
cd poppet
virtualenv .env
source .env/bin/activate
pip install -r requirements.txt
mkdir instance
mkdir logs
mkdir touch instance/__init__.py
cp instance_sample.py instance/config.py
mkdir -p unifispot/static/uploads/

cd "$BUILDDIR"

echo "-----------------------------Building Packages-----------------------------"
cd build 
fpm -s dir -t deb -n poppet -v 0.1 -d "nginx,redis-server,mysql-server,mysql-client,python-dev,libmysqlclient-dev,python-pip,git,bc"  --after-install poppet/scripts/post_install.sh  poppet/=/usr/share/nginx/poppet 
