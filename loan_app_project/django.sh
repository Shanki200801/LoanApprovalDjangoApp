#!/bin/bash
echo "Create migrations"
python manage.py makemigrations djangoapp
echo "=================================="

echo "Migrate"
python manage.py migrate
echo "=================================="

echo "Start server"
python manage.py runserver 0.0.0.0:8000 &
echo "==================================="

echo "Start Celery Worker"
celery -A loan_app_project worker --loglevel=info
echo "===================================="

