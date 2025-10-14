try:
	from .celery import app as celery_app
	__all__ = ('celery_app',)
except Exception:
	# Celery isn't installed in this environment — keep startup working without it
	celery_app = None
	__all__ = ()
