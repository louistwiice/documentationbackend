#!/bin/sh
python3 ./scripts/wait_for_postgres.py
python3 ./src/manage.py collectstatic --noinput
python3 ./src/manage.py migrate
#python3 ./src/manage.py runserver 0.0.0.0:8000
cd src && gunicorn config.wsgi:application --workers=2 --reload --bind 0.0.0.0:8000