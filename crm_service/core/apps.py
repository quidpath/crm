from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "crm_service.core"
    label = "crm_core"
    verbose_name = "Core (base models, utils, services)"
