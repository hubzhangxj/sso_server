# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = '51nq+jny--lu9(xt%9o+@-439vy79xr(!_%1a@8^kmsy5hckvs'

DEBUG = True

ALLOWED_HOSTS = ['*']


INSTALLED_APPS = (
    'suit',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'authen',
    'backend',
    'account',
    'backup',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'UAMS.urls'
WSGI_APPLICATION = 'UAMS.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'uams',
        'USER': 'uams',
        'PASSWORD': 'uams',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

LANGUAGE_CODE = 'zh-Hans'
LOCALE_PATHS = (os.path.join(BASE_DIR, 'locale'),)
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_L10N = True
USE_TZ = False
SESSION_COOKIE_AGE = 1800
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_NAME = "uams_sessionid"
CSRF_COOKIE_NAME = 'uams_csrftoken'
STATIC_URL = '/static/'
STATICFILES_DIRS = (os.path.join(BASE_DIR, "resources/static"),)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'resources/templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                "django.template.context_processors.i18n",
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'debug': DEBUG,
        },
    },
]
SUIT_CONFIG = {
    'ADMIN_NAME': 'UAMS后台',
    'LIST_PER_PAGE': 10,
    'MENU': (
        {'app': 'backend', 'label': u'后台管理', 'icon': 'icon-wrench'},
        {'app': 'account', 'label': u'账号管理', 'icon': 'icon-file'},
        {'app': 'backup', 'label': u'备份管理', 'icon': 'icon-tasks'},
    ),
}
LOGIN_REDIRECT_URL = "/"

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': [
            'localhost:11211',
        ],
        'TIMEOUT': 30,
    }
}

LDAP_SYNC_URL = 'http://192.168.4.30:7890/ldap/operate/'

AUTH_USER_MODEL = "account.Account"

# email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_SSL = True
EMAIL_HOST = 'smtp.qq.com'  # 'smtp.163.com'
EMAIL_PORT = 465
EMAIL_HOST_USER = 'uamsmgr@qq.com'  # 'estuaryadmin@163.com'
EMAIL_HOST_PASSWORD = 'emriensiybfgeaeb'
EMAIL_DEFAULT_FROM = 'UAMS <uamsmgr@qq.com>'  # 'Estuary <estuaryadmin@163.com>'
EMAIL_SUBJECT = 'UAMS account'
EMAIL_RESET_CONTENT = 'Dear <strong>USER</strong>, Your account has been moved to UAMS, and your password has ' \
                      'been reset. </br>A new password <strong>PWD</strong> is assigned to you, you can use this ' \
                      'password to login directly or you can reset your password with it.'

EMAIL_LOCK_CONTENT = 'Dear <strong>USER</strong>, Your account has been locked by administrator, your account is' \
                     ' not allowed to sign on UAMS.'
EMAIL_UNLOCK_CONTENT = 'Dear <strong>USER</strong>, Your account has been unlocked by administrator, you can' \
                     ' sign on UAMS now.'


LOG_PATH = os.path.join(BASE_DIR, 'log')
if not os.path.exists(LOG_PATH):
    os.mkdir(LOG_PATH)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'standard': {
            'format': '%(levelname)s %(asctime)s %(filename)s %(funcName)s %(lineno)d: %(message)s'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'standard'
        },
        'file_handler': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(LOG_PATH, 'sys.log'),
            'formatter': 'standard'
        },  # 用于文件输出
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file_handler', 'console'],
            'level': 'WARNING',
            'propagate': True  # 是否继承父类的log信息
        },
        # 'django.request': {
        #     'handlers': ['mail_admins'],
        #     'level': 'ERROR',
        #     'propagate': False,
        # },
        'custom': {
            'handlers': ['file_handler', 'console'],
            'level': 'DEBUG',
            'propagate': True
        }
    }
}

