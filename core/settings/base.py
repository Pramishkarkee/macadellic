import os, environ
import sys
from pathlib import Path

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)
# BASE_DIR = os.path.dirname(os.path.dirname(__file__))
BASE_DIR=Path(__file__).resolve(strict=True).parent.parent.parent
# CORE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORE_DIR =BASE_DIR
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))


SECRET_KEY = env('SECRET_KEY', default='S#perS3crEt_007')

DEBUG = env('DEBUG')

ASSETS_ROOT = os.getenv('ASSETS_ROOT', '/static/assets')

ALLOWED_HOSTS=['*']

CSRF_TRUSTED_ORIGINS = ['http://localhost:85', 'http://127.0.0.1', 'https://' + env('SERVER', default='127.0.0.1')]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.home',  # Enable the inner home (home)
    'apps.authentication',
    'apps.accounts',
    'apps.checkout',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.github',
    'allauth.socialaccount.providers.twitter',
    "sslserver"
]

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.github',
    'allauth.socialaccount.providers.twitter',
    "sslserver"
]

LOCAL_APPS = [
    'apps.home',  # Enable the inner home (home)
    'apps.authentication',
    'apps.accounts',
    'apps.checkout',
]

INSTALLED_APPS = DJANGO_APPS+THIRD_PARTY_APPS+LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "django.middleware.common.BrokenLinkEmailsMiddleware",
]

ROOT_URLCONF = 'core.urls'
LOGIN_REDIRECT_URL = "home"  # Route defined in home/urls.py
LOGOUT_REDIRECT_URL = "home"  # Route defined in home/urls.py
TEMPLATE_DIR = os.path.join(CORE_DIR, "apps/templates")  # ROOT dir for templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.context_processors.cfg_assets_root',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_ROOT = os.path.join(CORE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Extra places for collectstatic to find static files.

STATICFILES_DIRS = (
    os.path.join(CORE_DIR, 'apps/static'),
)
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'authentication.CustomUser'

FTP_UPLOAD = False

if os.getenv("FTP_UPLOAD", default=False):
    try:
        DEFAULT_FILE_STORAGE = os.getenv("upload_cloud_type")
        ftp_username = os.getenv("ftp_username")
        ftp_password = os.getenv("ftp_password")
        ftp_server_url = os.getenv("ftp_server_url")
        ftp_port = os.getenv("ftp_port")
        FTP_STORAGE_LOCATION = f'ftp://{ftp_username}:{ftp_password}@{ftp_server_url}:{ftp_port}'

        # Enable the feature
        FTP_UPLOAD = True
    except Exception as _:

        FTP_UPLOAD = False
        print('FTP credentials not set in the environment')

AUTHENTICATION_BACKENDS = (
    # "core.custom-auth-backend.CustomBackend",
    'django.contrib.auth.backends.ModelBackend',
    "allauth.account.auth_backends.AuthenticationBackend",
)


SITE_ID = 6

ACCOUNT_EMAIL_VERIFICATION = 'none'

SERVER = env('SERVER', default='localhost')

if DEBUG:
    ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'http' if sys.argv[1] == 'runserver' else 'https'
else:
    ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'  # assumed production http protocol is https

LOGIN_REDIRECT_URL = f'{ACCOUNT_DEFAULT_HTTP_PROTOCOL}://localhost:{8000 if DEBUG else 80}/'

