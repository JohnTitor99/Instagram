from django.apps import AppConfig


class DirectConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'direct'
    name = 'apps.direct'
