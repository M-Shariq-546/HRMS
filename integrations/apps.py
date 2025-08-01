from django.apps import AppConfig


class IntegrationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'integrations'


    def ready(self):
        from integrations import scheduler
        scheduler.start()