release: python manage.py migrate --noinput
web: gunicorn --bind :$PORT --workers 4 --worker-class --loglevel=INFO uvicorn.workers.UvicornWorker dtb.asgi:application
worker: celery -A dtb worker -P prefork --loglevel=INFO
beat: celery -A dtb beat --loglevel=INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
