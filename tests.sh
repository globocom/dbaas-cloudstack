#!/bin/bash
echo -n 'waiting mysql start'
while ! mysql -h $DBAAS_DATABASE_HOST -uroot -p$DBAAS_DATABASE_PASSWORD -e "SHOW DATABASES"
do
  echo -n .
  sleep 1
done

echo 'MYSQL STARTED!!!!'

# Create DATABASE
echo "create database IF NOT EXISTS dbaas;" | mysql -h $DBAAS_DATABASE_HOST -uroot -p$DBAAS_DATABASE_PASSWORD

# Create user on mongo
python /code/dbaas_cloudstack/add_user_admin_on_mongo.py

# TODO: verify is this code already on file
echo "NOSE_ARGS.extend(['--tests=/code/dbaas_cloudstack/'])" >> /code/dbaas/dbaas/dbaas/settings_test.py

cat /code/dbaas/dbaas/dbaas/settings_test.py

# Run tests
cd /code/dbaas/dbaas && python manage.py test --settings=dbaas.settings_test --traceback

# bash
