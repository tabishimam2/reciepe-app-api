#!/bin/sh

set -e

python manage.py wait_for_db
python manage.py collectstatic --noinput
python mange.py migrate

uwsgi --sockert:9000 --workers 4 --master --enable-threads --module app.wsgi