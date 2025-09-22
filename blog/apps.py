from django.apps import AppConfig


class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog'

    def ready(self):
        # Import signal handlers
        try:
            from . import signals  # noqa: F401
        except Exception:
            pass
