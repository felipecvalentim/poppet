echo "---delete all files and folders----"
rmdir migrations /s /q
rmdir migrations_test /s /q


del instance\database_dev.db
del instance\database_test.db



echo "-----Initialize all DBs------------"
python manage.py db init
python manage.py db migrate
python manage.py db upgrade


python test_manage.py db init
python test_manage.py db migrate
python test_manage.py db upgrade