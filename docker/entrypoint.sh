python manage.py server_init || exit 1
exec supervisord -c /config/supervisord.conf