from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    
    def ready(self):
        # Import signal handlers to register post_save hooks
        try:
            from . import signals  # noqa: F401
        except Exception:
            # If signals fail to import during some management tasks, don't break startup
            pass
        # Import checks so Django can run core checks (like VAPID presence)
        try:
            from . import checks  # noqa: F401
        except Exception:
            pass
