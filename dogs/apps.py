# dogs/apps.py

from django.apps import AppConfig


class DogsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dogs'
    verbose_name = 'Кинологическая служба'