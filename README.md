# "Game News Site"

### Run 
```bash
cd..
.venv\Scripts\activate
cd game-news-site
py manage.py runserver 0.0.0.0:8024 --settings=app.settings.local
```

## Pet project (Python Django 4.2.11)

## Front:
HTML/CSS/JS/HTMX
CKEDITOR 5

## Backend
Python 3.11
Django 4.2.11
PostgreSQL

# Python Modules
```bash
py -m pip install "uvicorn[standard]"    # ASGI server для django
py -m pip install gunicorn               # ASGI server для django
py -m pip install psycopg2               # PostgreSQL
py -m pip install python-dotenv          # для змінних середоввища в файлі .env
py -m pip install django-environ         # для змінних середоввища в файлі .env для django
py -m pip install django-debug-toolbar   # для дебага django
py -m pip install django-jet-reboot      # крута адмін панель
py -m pip install social-auth-app-django # кастомна авторизація (google, facebook, github)
py -m pip install django-allauth         # звичайна та кастомна авторизація
py -m pip install django-simple-captcha  # текстова капча
py -m pip install django-recaptcha       # капча-кнопка google
py -m pip install django-phonenumber-field # телефон (поле моделі)
py -m pip install django-colorfield      # колір(поле моделі)
py -m pip install mypy                   # для перевірки коду
py -m pip install humanize               # для преображення текста (роди і тд)
py -m pip install mimesis                # для фейкової інфи
py -m pip install bleach                 # для очищення html від xss
py -m pip install celery                 # менеджер задач
py -m pip install pytils                 # перетворення кирилиці в slug
py -m pip install djangorestframework    # DRF
py -m pip install markdown               # DRF Markdown support for the browsable API.
py -m pip install django-filter          # DRF Filtering support
py -m pip install termcolor              # Colored console output
py -m pip install django-ckeditor-5      # Заповлення форматованого текста ckeditor 5
py -m pip install beautifulsoup4         # Для видалення тегів html з текста
py -m pip install django-filebrowser     # Файловий менеджер проекта для адмінки
py -m pip install django-compressor      # робота з css scss sass
py -m pip install django-bootstrap5      # стилі bootstrap 5
py -m pip install django-admin-interface # стилі для адмінки
py -m pip install django-gm2m            # функціонал для полів m2m
py -m pip install django-cities-light    # всі міста
py -m pip install drf-spectacular        # Документація для REST API
py -m pip install pillow                 # робота з зображеннями
# Тестування (вбудований unittest)
py -m pip install pytests                # unittests тестування
py -m pip install selenium               # тестування в браузері
```

```bash
[Add fake posts](http://127.0.0.1:8024/api/fake)
```
