from django.apps import AppConfig

class VehiclesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "vehicles"

    def ready(self):
        from django.apps import apps
        Vehicle = apps.get_model("vehicles", "Vehicle")  # ✅ Chargement retardé