from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# AUTH_USER_MODEL = 'leads.User'
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-43+xrratu4w0s2)38aopnf5-_g9m-4ibpq58+afhail$7^gj8v'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'songs',
    'leads',
    'posts',
    'agents',

    # third party packages
    'mptt',
    'django_browser_reload',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'tailwind',
    # 'themw',
    'rest_framework',
    'rest_framework.authtoken',
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

ROOT_URLCONF = 'musics.urls'

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
        },
    },
]

WSGI_APPLICATION = 'musics.wsgi.application'


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

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'songs.User'

MUSIC_TITLE_MAX_LENGTH = 50

SITE_ID = 1

INTERNAL_IPS = [
    "127.0.0.1",
]

# EMAIL CONFIG:
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# TAILWIND_APP_NAME = 'themw'

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login'

# ACCOUNT_EMAIL_REQUIRED = True


# NPM_BIN_PATH = "/Program Files/nodejs/node_modules/npm/bin/npm.cmd"
