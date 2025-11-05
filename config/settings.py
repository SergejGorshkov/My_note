import os
import sys
from pathlib import Path

from celery.schedules import crontab
from dotenv import load_dotenv

# Указывает на корневую папку проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# Загрузка переменных окружения из файла .env
load_dotenv(override=True)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")  # Ключ Django для подписи сессий

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True if os.getenv("DEBUG") == "True" else False

ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_celery_beat",
    "users",
    "my_note",

]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.locale.LocaleMiddleware",  # Для автоматического определения зоны пользователя
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER", default="postgres"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("POSTGRES_HOST", default="localhost"),
        "PORT": os.getenv("POSTGRES_PORT", default="5432"),
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'ru-ru'  # Автоматическое форматирование даты и времени в русском формате (ДД.ММ.ГГГГ ЧЧ:ММ)

TIME_ZONE = "Europe/Moscow"  # Настройка временной зоны

USE_I18N = True  # Включает поддержку интернационализации.

USE_L10N = True  # Включает поддержку локализации, применяя форматирование даты и времени.

USE_TZ = True  # Включение поддержки временных зон

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = "/static/"  # Маршрут к папке со статическими файлами
STATICFILES_DIRS = [BASE_DIR / "static"]  # Список папок на диске, из которых будут подгружаться статические файлы
STATIC_ROOT = BASE_DIR / "staticfiles"  # Папка, куда собираются все стат. файлы для продакшена командой collectstatic

MEDIA_URL = "/media/"  # Путь к папке с медиафайлами
MEDIA_ROOT = BASE_DIR / "media"  # Путь к папке на диске с медиафайлами, загружаемыми пользователем

# Настройки приложения для защиты от DoS-атак через отправку больших объемов данных:
# Ограничение размера данных форм и JSON, которые обрабатываются в оперативной памяти.
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
# Ограничение размера загружаемых файлов, которые сохраняются на диске.
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
# Максимальное количество полей в форме/JSON
DATA_UPLOAD_MAX_NUMBER_FIELDS = 150
# Максимальное количество файлов, которые будут храниться в оперативной памяти при множественной загрузке файлов.
FILE_UPLOAD_MAX_MEMORY_FILES = 10

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"  # По умолчанию используется BigAutoField для первичных ключей

# Авторизация в приложении users (для использования собственного класса пользователя)
AUTH_USER_MODEL = "users.User"  # Для аутентификации используется собственный класс User
LOGIN_REDIRECT_URL = 'my_note:home'  # После успешной авторизации перенаправление на главную страницу приложения
LOGOUT_REDIRECT_URL = 'my_note:home'  # После выхода из аккаунта перенаправление на главную страницу приложения
LOGIN_URL = 'users:login'  # Путь к странице логина для перенаправления неавторизованных пользователей при попытке
# перехода на защищенные страницы

# Настройки для Celery

# URL-адрес брокера сообщений
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")  # Например, Redis, который по умолчанию работает на порту 6379
# URL-адрес брокера результатов, также Redis
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")
# Часовой пояс для работы Celery
CELERY_TIMEZONE = TIME_ZONE  # временная зона (совпадает с временной зоной в Django)
# Флаг отслеживания выполнения задач
CELERY_TASK_TRACK_STARTED = True
# Максимальное время на выполнение задачи
CELERY_TASK_TIME_LIMIT = 10 * 60  # 10 минут
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# Настройки для django-celery-beat
# Настройка расписания выполнения задач для Celery
CELERY_BEAT_SCHEDULE = {
    "send-note-reminders": {
        "task": "users.tasks.send_reminder_message",  # Путь к задаче
        "schedule": crontab(hour=20, minute=0),  # Выполняется каждый день в 20:00 (по Москве)
    },
}
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

TELEGRAM_URL = "https://api.telegram.org/bot"  # URL для отправки сообщений в Telegram
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")  # Токен бота Telegram

# Redis cache
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Настройка отправки почты через сервер Яндекса
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_PORT = 465
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')  # Адрес электронной почты для отправки почты
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')  # Пароль от сервиса яндекса для отправки почты
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER  # По умолчанию отправляем письма с этого адреса

# Для тестирования (использует консоль вместо реальной отправки)
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Динамически настраивает базу данных для тестов в Django проекте
# Проверяет, присутствует ли 'test' в аргументах командной строки. Используется SQLite вместо основной БД
if 'test' in sys.argv:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',  # Используется SQLite вместо основной БД
            'NAME': BASE_DIR / 'db.sqlite3',  # Файл БД SQLite в корне проекта
        }
    }
