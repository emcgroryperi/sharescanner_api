#!/bin/sh

until python manage.py makemigrations
do
    echo "Waiting for db to make migrations"
    sleep 2
done

until python manage.py migrate
do
    echo "Waiting for db to be ready..."
    sleep 2
done

# python manage.py collectstatic --noinput

# python manage.py createsuperuser --noinput

# for debug
python manage.py runserver 0.0.0.0:8000