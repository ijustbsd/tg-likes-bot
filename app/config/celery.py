import celery

from app.config.settings import CELERY_BROKER_URL

app = celery.Celery("bot", broker=CELERY_BROKER_URL)

app.autodiscover_tasks()
