FROM python:3.11.7-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN mkdir /app /app/staticfiles /app/media

WORKDIR /app

RUN pip install --upgrade pip
COPY requirements.txt /app/

RUN cat /app/requirements.txt \
    && apt-get update \
    && apt-get -y install libpq-dev gcc gettext \
    && pip install -r requirements.txt

COPY . /app/

EXPOSE 8024

