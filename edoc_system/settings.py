"""
Django settings for edoc_system project.
File-based authentication system adapted from NPU guide.
"""

import os
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-in-production-123456789')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=lambda v: [s.strip() for s in v.split(',')])

# Base URL for QR Code verification
BASE_URL = config('BASE_URL', default='http://localhost:8002')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',  # Add humanize for number formatting

    # Third-party apps
    'django_summernote',  # WYSIWYG Editor

    # Local apps
    'accounts.apps.AccountsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'edoc_system.urls'

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

WSGI_APPLICATION = 'edoc_system.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME', default='your_database_name'),
        'USER': config('DB_USER', default='your_database_user'),
        'PASSWORD': config('DB_PASSWORD', default='your_database_password'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# SQLite fallback for development (uncomment if needed)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }


# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Authentication Backends
AUTHENTICATION_BACKENDS = [
    'accounts.backends.HybridAuthBackend',  # Primary: Hybrid MySQL + NPU API
    'django.contrib.auth.backends.ModelBackend',  # Fallback: Django default (for superusers)
]


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
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

LANGUAGE_CODE = 'th'
TIME_ZONE = 'Asia/Bangkok'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# NPU API Configuration
NPU_API_BASE_URL = config('NPU_API_BASE_URL', default='https://api.npu.ac.th/v2/ldap/')
NPU_API_AUTH_ENDPOINT = config('NPU_API_AUTH_ENDPOINT', default='auth_and_get_personnel/')
NPU_API_TOKEN = config('NPU_API_TOKEN', default='your_npu_api_token_here')
NPU_API_TIMEOUT = config('NPU_API_TIMEOUT', default=30, cast=int)  # seconds

# NPU API Settings
NPU_API_SETTINGS = {
    'base_url': NPU_API_BASE_URL,
    'auth_endpoint': NPU_API_AUTH_ENDPOINT,
    'token': NPU_API_TOKEN,
    'timeout': NPU_API_TIMEOUT,
    'headers': {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {NPU_API_TOKEN}',
    }
}

# NPU Student API Configuration
NPU_STUDENT_API_BASE_URL = config('NPU_STUDENT_API_BASE_URL', default='https://api.npu.ac.th/v2/ldap/')
NPU_STUDENT_API_AUTH_ENDPOINT = config('NPU_STUDENT_API_AUTH_ENDPOINT', default='auth_and_get_student/')
NPU_STUDENT_API_TOKEN = config('NPU_STUDENT_API_TOKEN', default='your_npu_student_api_token_here')
NPU_STUDENT_API_TIMEOUT = config('NPU_STUDENT_API_TIMEOUT', default=30, cast=int)  # seconds

# NPU Student API Settings
NPU_STUDENT_API_SETTINGS = {
    'base_url': NPU_STUDENT_API_BASE_URL,
    'auth_endpoint': NPU_STUDENT_API_AUTH_ENDPOINT,
    'token': NPU_STUDENT_API_TOKEN,
    'timeout': NPU_STUDENT_API_TIMEOUT,
    'headers': {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {NPU_STUDENT_API_TOKEN}',
    }
}

# File-based Authentication Settings (Legacy - kept for fallback)
USERS_FILE_PATH = config('USERS_FILE_PATH', default=os.path.join(BASE_DIR, 'data', 'users.csv'))


# Security Settings (for production)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    
# Session Settings
SESSION_COOKIE_HTTPONLY = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 3600  # 1 hour

# CSRF Settings
CSRF_COOKIE_HTTPONLY = True

# Email Settings (for notifications)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Development
# For production:
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = config('EMAIL_HOST')
# EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = config('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
# DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')


# Messages Framework
from django.contrib.messages import constants as messages

MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'error',
}


# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'accounts': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Create logs directory if it doesn't exist
os.makedirs(BASE_DIR / 'logs', exist_ok=True)


# Summernote Configuration
SUMMERNOTE_CONFIG = {
    # Using SummernoteWidget - iframe mode
    'iframe': True,

    # Set height of editor
    'height': '300',
    'width': '100%',

    # Toolbar customization
    'toolbar': [
        ['style', ['style']],
        ['font', ['bold', 'underline', 'italic', 'clear']],
        ['fontname', ['fontname']],
        ['fontsize', ['fontsize']],
        ['color', ['color']],
        ['para', ['ul', 'ol', 'paragraph']],
        ['table', ['table']],
        ['insert', ['link']],
        ['view', ['fullscreen', 'codeview', 'help']],
    ],

    # Language
    'lang': 'th-TH',

    # Disable attachment (file upload)
    'disable_attachment': True,

    # Custom CSS for Thai fonts
    'css': (
        '//fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap',
    ),

    # Summernote options
    'summernote': {
        'fontNames': ['Sarabun', 'THSarabunNew', 'Arial', 'Tahoma'],
        'fontNamesIgnoreCheck': ['Sarabun', 'THSarabunNew'],
        'lineHeights': ['1.0', '1.2', '1.4', '1.5', '1.6', '1.8', '2.0'],
    }
}