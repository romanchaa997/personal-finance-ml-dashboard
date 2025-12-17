web: gunicorn dashboard.main:app
worker: python -m celery -A core.tasks worker
