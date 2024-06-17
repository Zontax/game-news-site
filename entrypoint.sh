#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

python manage.py makemigrations --settings=app.settings.local
python manage.py migrate --settings=app.settings.local
python manage.py collectstatic --no-input --settings=app.settings.local
python manage.py makemessages -l uk --settings=app.settings.local
python manage.py compilemessages --settings=app.settings.local

exec "$@"
