FROM python:3.7.3-stretch

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

RUN chmod +x /app/django.sh

ENTRYPOINT ["/app/django.sh"]
# ENTRYPOINT ["/bin/sh", "-c", "/app/django.sh && celery -A loan_app_project worker --loglevel=info"]
# Start Celery worker at launch
# CMD ["sh", "-c", "/app/django.sh && celery -A loan_app_project worker --loglevel=info"]