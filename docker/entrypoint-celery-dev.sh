export DEBUG=True
python3 manage.py server_init || exit 1
celery -A ddl worker -l info -Q result --concurrency=1