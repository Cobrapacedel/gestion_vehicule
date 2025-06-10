from django.apps import AppConfig

class TollsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tolls"

    def ready(self):
        import tolls.signals  # Import des signaux pour les notifications