import os
from django.apps import AppConfig


class HelpdeskConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "helpdesk"

    def ready(self):
        from django.urls import include, path

        from horilla.horilla_settings import APPS
        from horilla.urls import urlpatterns
        APPS.append("helpdesk")
        urlpatterns.append(
            path("helpdesk/", include("helpdesk.urls")),
        )
        super().ready()
        if os.environ.get('RUN_MAIN') == 'true':
            from helpdesk.scheduler import start
            start()
