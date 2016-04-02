echo "---delete all files and folders----"
rm -rf migrations 

mysqladmin -uroot -p drop poppet

mysql -u root -p -e "create database poppet"; 
echo "-----Initialize all DBs------------"
python manage.py db init
python manage.py db migrate
python manage.py db upgrade
python manage.py init_data


