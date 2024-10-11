import logging
import os
from pathlib import Path
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# 固定 IP 地址，确保与路由器中设置的静态 IP 地址相同
fixed_ip = '192.168.1.100'  # 將這個 IP 設置為固定的主機 IP

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-y&%10_w2a%0v)(jqe46d2)mevjv0f^ro8!#+pu#67d%md8k8vr'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# 設定允許的主機，包括本機和 Bluestacks 的 IP 地址
ALLOWED_HOSTS = ['0.0.0.0', '127.0.0.1', 'localhost', fixed_ip, '192.168.168.87', '192.168.168.109', '172.16.32.106']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_otp',
    'django_otp.plugins.otp_totp',
    'django_otp.plugins.otp_static',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'app113209.apps.App113209Config',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # 確保放在 SessionMiddleware 之上
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'app113209.middleware.allow_iframe.AllowIframeMiddleware',
]

ROOT_URLCONF = 'project113209.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'project113209.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '113-ntub113209',
        'USER': 'ntub113209',
        'PASSWORD': 'Sw@23110565',
        'HOST': '140.131.114.242',
        'PORT': '3306',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'app113209.validators.CustomPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Taipei'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
    BASE_DIR / 'vue-admin' / 'dist',
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Login and Redirect URLs
LOGIN_URL = '/frontend/login/'
LOGIN_REDIRECT_URL = '/frontend/home/'
LOGOUT_REDIRECT_URL = '/frontend/login/'

# 後台設定
BACKEND_LOGIN_URL = '/backend/login/'
BACKEND_LOGIN_REDIRECT_URL = '/backend/management/'
BACKEND_LOGOUT_REDIRECT_URL = '/backend/login/'

# 自定義用戶模型
AUTH_USER_MODEL = 'app113209.User'

# Logging Configuration
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s',
)

# Email settings for password reset and verification
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'leewesley527@gmail.com'
EMAIL_HOST_PASSWORD = 'evcajuubazrginrn'

# Session settings
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 60 * 30
SESSION_COOKIE_SECURE = False  # 開發模式下設置為 False
SESSION_COOKIE_HTTPONLY = True
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
SESSION_COOKIE_NAME = 'sessionid'

# Cache settings
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# 認證後端
AUTHENTICATION_BACKENDS = (
    'app113209.backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
)

# Django REST Framework 設定
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        # 'djangorestframework_camel_case.render.CamelCaseJSONRenderer',
        # 'djangorestframework_camel_case.render.CamelCaseBrowsableAPIRenderer',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
        # 'djangorestframework_camel_case.parser.CamelCaseJSONParser',

    ],
}

# JWT 配置
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}

# CORS 配置
CORS_ALLOW_ALL_ORIGINS = True  # 開發環境中允許所有來源
CORS_ALLOW_CREDENTIALS = True  # 允許傳遞憑證

# CSRF 配置
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8080",
    "http://192.168.1.100:8080",  # 本機固定 IP
    "http://192.168.168.87:8080",  # Bluestacks 固定 IP
    "http://192.168.168.109:8080"
]

# Logging 設置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}

# Media files
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
