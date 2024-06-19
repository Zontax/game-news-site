FROM python:3.11.7-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN mkdir /app /app/staticfiles /app/media

WORKDIR /app

RUN pip install --upgrade pip
COPY requirements.txt /app/

RUN cat /app/requirements.txt \
    && apt-get update \
    && apt-get -y install gcc pkg-config libpq-dev gettext \
    && pip --no-cache-dir install -r requirements.txt \
    && apt-get remove -y gcc pkg-config \
    && rm -rf /var/lib/apt/lists/*
COPY . /app/

ENTRYPOINT ["/app/entrypoint.sh"]

EXPOSE 8024
