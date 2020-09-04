web: gunicorn buddychat.wsgi --preload --log-file -
chat: daphne buddychat.asgi:channel_layer --port $PORT --bind 0.0.0.0 -v2
chatworker: python manage.py runworker --settings=buddychat.settings -v2
release: python manage.py migrate