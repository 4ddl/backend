export DEBUG=True
python3 manage.py server_init || exit 1
celery -A ddl worker -l info -Q result,judge --concurrency=1