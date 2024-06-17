FROM python:3.11.7-slim as base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN mkdir /app
RUN mkdir /app/staticfiles
WORKDIR /app

RUN pip install --upgrade pip
COPY requirements.txt /app/
RUN cat /app/requirements.txt

RUN apt-get update && apt-get -y install libpq-dev gcc gettext

RUN pip install -r requirements.txt
COPY . /app/

EXPOSE 8024

# CMD ["gunicorn", "app.wsgi:application", "--bind", "0.0.0.0:8024", "--workers", "4", "--threads", "4", "--env", "DJANGO_SETTINGS_MODULE=app.settings.local"]
