release: python manage.py migrate --noinput
web: gunicorn dtb.wsgi:application --bind :$PORT
worker: celery -A dtb worker -P prefork --loglevel=INFO
beat: celery -A dtb beat --loglevel=INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler


# We can use asgi, but then bugs appear when sending many images in ConversationHandler
# web: gunicorn --bind :$PORT --workers 2 --worker-class uvicorn.workers.UvicornWorker dtb.asgi:application