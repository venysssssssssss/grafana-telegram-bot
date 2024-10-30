from celery import Celery

# Configura o Celery com o Redis como backend e broker
celery_app = Celery(
    'tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0',
)

celery_app.conf.update(
    task_track_started=True,
    result_expires=3600,
)
