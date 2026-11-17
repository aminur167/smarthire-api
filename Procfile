web: gunicorn smarthire.wsgi:application --bind 0.0.0.0:$PORT
worker: celery -A smarthire.celery_app worker -l info
