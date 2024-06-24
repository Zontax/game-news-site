FROM python:3.11-alpine3.20

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN mkdir /app /app/staticfiles /app/media

WORKDIR /app

RUN pip install --upgrade pip
COPY requirements.txt /app/

RUN cat /app/requirements.txt \
    && apk update \
    && apk add --no-cache gcc pkgconf libpq-dev gettext build-base \
    && pip --no-cache-dir install -r requirements.txt \
    && apk del --no-cache build-base
COPY . /app/

ENTRYPOINT ["/app/entrypoint.sh"]

EXPOSE 8024
