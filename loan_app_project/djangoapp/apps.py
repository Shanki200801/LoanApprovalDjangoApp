# apps.py in djangoapp
from django.apps import AppConfig
from .tasks import ingest_excel_data


class DjangoappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "djangoapp"

    def ready(self):
        # Call the Celery task when the Django application is ready
        ingest_excel_data.delay(
            file_path=["./djangoapp/customer_data.xlsx", "./djangoapp/loan_data.xlsx"]
        )
