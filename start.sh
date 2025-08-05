python manage.py migrate --no-input &&
gunicorn core.wsgi:application --log-file -
