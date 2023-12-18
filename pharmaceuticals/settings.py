from decouple import Csv, config
from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# AUTH_USER_MODEL = 'leads.User'
# SECURITY WARNING: keep the secret key used in production secret!

SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'daphne',  # for ASGI server
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

 
    'songs',
    'leads',
    'chats',
    'posts',
    'agents',
    'pharmcare',
    'staff',

    # third party packages
    "chatterbot.ext.django_chatterbot",
    'mptt',
    'django_browser_reload',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'tailwind',
    'django_countries',
    'sass_processor',
    # 'themw', # tailwind-css-for-django
    'crispy_forms',
    'crispy_tailwind',
    'compressor',
    'rest_framework',
    'rest_framework.authtoken',
    'tinymce',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "allauth.account.middleware.AccountMiddleware",
    "django_browser_reload.middleware.BrowserReloadMiddleware",
]

ROOT_URLCONF = 'pharmaceuticals.urls'

""" 
import redis

r = redis.Redis(host='localhost', port=6379, db=0)
r.set('foo', 'bar') and r.get('foo') """

# Celery
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL").strip()
CELERY_RESULT_BACKEND = os.getenv("REDIS_BACKEND").strip()


# Chatterbot
CHATTERBOT = {
    "name": "Medconnect Agent",
    "logic_adapters": [
        "chatterbot.logic.BestMatch",
    ],
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [os.getenv("REDIS_BACKEND")],
            # "hosts": [("localhost", 6379)],
        },
    },
}


# CORS CONFIGURATIONS :
CORS_ORIGIN_ALLOW_ALL = True

ALLOWED_HOSTS = [
    '127.0.0.1'
]

CORS_ALLOWED_ORIGIN = [
    'http://127.0.0.1', 'localhost'
]

CORS_ALLOW_CREDENTIALS = False

CORS_ALLOW_HEADERS = [
    'accept'
    'accept-encoding',
    'authorization',
    'content-type',
    'origin',
    'dnt',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

CORS_ALLOW_METHOD = [
    'GET',
    'POST',
    'PUT',
    'DELETE',
    'OPTIONS',
    'PATCH',
]


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'builtins': [
                'crispy_forms.templatetags.crispy_forms_tags',
                'crispy_forms.templatetags.crispy_forms_field'
            ]
        },

    },
]


ASGI_APPLICATION = "pharmaceuticals.asgi.application"


WSGI_APPLICATION = 'pharmaceuticals.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
ENVIRONMENT = os.getenv("ENVIRONMENT")
if DEBUG == True:

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

if not DEBUG:
    DATABASES = {
        'default': {
            "ENGINE": 'django.db.backends.mysql',
            "NAME": '',
            "USER": 'root',
            "PASSWORD": "",
            "HOST": "localhost",
            "PORT": 3306

        }
    }

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
    'sass_processor.finders.CssFinder',
    'compressor.finders.CompressorFinder',
)

COMPRESS_OFFLINE = True

SASS_PROCESSOR_INCLUDE_DIRS = [
    BASE_DIR / 'node_modules',
]

COMPRESS_ROOT = BASE_DIR / 'static'

COMPRESS_ENABLED = True


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = 'static_root'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
TEMPLATE_DEBUG = True


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'songs.User'

MUSIC_TITLE_MAX_LENGTH = os.getenv('MUSIC_TITLE_MAX_LENGTH')
FROM_EMAIL = os.getenv('FROM_EMAIL')

SITE_ID = 1

INTERNAL_IPS = [
    "127.0.0.1",
]

# EMAIL CONFIG:
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# TAILWIND_APP_NAME = 'themw'

LOGIN_REDIRECT_URL = '/leads'
LOGIN_URL = '/login'
LOGOUT_REDIRECT_URL = '/leads'

# ACCOUNT_EMAIL_REQUIRED = True


# NPM_BIN_PATH = "/Program Files/nodejs/node_modules/npm/bin/npm.cmd"

CRISPY_TEMPLATE_PACK = 'tailwind'
CRISPY_ALLOWED_TEMPLATE_PACK = 'tailwind'

# WHATSAPP
WHATSAPP_LINK = os.getenv('WHATSAPP_LINK')
