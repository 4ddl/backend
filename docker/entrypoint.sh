python3 manage.py server_init || exit 1
daphne -b 0.0.0.0 -p 8000 --proxy-headers ddl.asgi:application
