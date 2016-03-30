echo "---delete all files and folders----"

cd ..
rm -rf migrations_test 
rm -rf instance/database_test.db
echo "-----Initialize all DBs------------"
python test_manage.py db init
python test_manage.py db migrate
python test_manage.py db upgrade


