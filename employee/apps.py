"""
apps.py
"""
import os
from horilla.utils.logger import HorillaLogger
from django.apps import AppConfig

logger = HorillaLogger("employee.apps")


class EmployeeConfig(AppConfig):
    """
    AppConfig for the 'employee' app.

    This class represents the configuration for the 'employee' app. It provides
    the necessary settings and metadata for the app.

    Attributes:
        default_auto_field (str): The default auto field to use for model field IDs.
        name (str): The name of the app.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "employee"
    
    def ready(self):
        """
        Runs once Django app is ready. Starts the birthday scheduler.
        Prevents re-running in multiple processes (e.g., during migrations).
        """
        logger.info("Initializing Employee app scheduler...")
        from .birthday_notification_scheduler import start  # Import here to avoid premature model loading
        start()
        logger.info("Employee app scheduler started successfully")
