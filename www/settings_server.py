# -*- coding: utf-8 -*-

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

# 配置是否采用本地模式
LOCAL_FLAG = False

# 引入父目录来引入其他模块
import os
import sys
SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.extend([os.path.abspath(os.path.join(SITE_ROOT, '../'))])

SERVER_NAME = 'ZHIXUAN_WEB0' if not LOCAL_FLAG else 'DEVELOPER'
SERVER_DOMAIN = 'zhixuan.com'
MAIN_DOMAIN = 'http://www.%s' % SERVER_DOMAIN
IMG0_DOMAIN = 'http://img0.zhixuan.com'    # 'http://zimg0.qiniudn.com'

EMAIL_FROM = u'"智选" <service@zhixuan.com>'
EMAIL_HOST_USER = 'service@zhixuan.com'
EMAIL_HOST_PASSWORD = 'zhixuan2013'
EMAIL_HOST = 'smtp.exmail.qq.com'
EMAIL_PORT = '25'
NOTIFICATION_EMAIL = ['web@zhixuan.com']

if LOCAL_FLAG:
    DB_USER, DB_PWD, DB_HOST = '', '', ''
else:
    DB_USER, DB_PWD, DB_HOST = '****', '****', '****'
ACCOUNT_DB = 'account'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'www',                      # Or path to database file if using sqlite3.
        'USER': DB_USER,                      # Not used with sqlite3.
        'PASSWORD': DB_PWD,                  # Not used with sqlite3.
        'HOST': DB_HOST,                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    },
    'account': {
        'ENGINE': 'django.db.backends.mysql',  # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'account',                      # Or path to database file if using sqlite3.
        'USER': DB_USER,                      # Not used with sqlite3.
        'PASSWORD': DB_PWD,                  # Not used with sqlite3.
        'HOST': DB_HOST,                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    },
    'question': {
        'ENGINE': 'django.db.backends.mysql',  # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'question',                      # Or path to database file if using sqlite3.
        'USER': DB_USER,                      # Not used with sqlite3.
        'PASSWORD': DB_PWD,                  # Not used with sqlite3.
        'HOST': DB_HOST,                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    },
}

DATABASE_ROUTERS = ['www.account.router.AccountRouter', 'www.question.router.QuestionRouter']


TIME_ZONE = 'Asia/Shanghai'
LANGUAGE_CODE = 'zh-cn'
DATE_FORMAT = 'Y-m-d'
DATETIME_FORMAT = 'Y-m-d G:i:s'
SITE_ID = 1
USE_I18N = True
USE_L10N = True
MEDIA_ROOT = os.path.abspath(os.path.join(SITE_ROOT, '../static'))
MEDIA_URL = '/static/' if LOCAL_FLAG else ('http://static.%s/' % SERVER_DOMAIN)
STATIC_ROOT = ''
STATIC_URL = '/static/'
ADMIN_MEDIA_PREFIX = '/static/admin/'

STATICFILES_DIRS = (
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    # 'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'ud-9^7=s3eot_id*ltpnklid3tfr*w@z5x#1y0^hn6enfr+@i4'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    # 'django.template.loaders.app_directories.Loader',
    # 'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    # "django.core.context_processors.debug",
    # "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    # "django.core.context_processors.static",
    "django.core.context_processors.request",
    "www.misc.context_processors.config",
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # 'django.contrib.messages.middleware.MessageMiddleware',
    'www.middleware.user_middleware.UserMiddware'
)

ROOT_URLCONF = 'www.urls'

TEMPLATE_DIRS = (
    os.path.abspath(os.path.join(SITE_ROOT, 'templates')),
)

INSTALLED_APPS = (
    # 'django.contrib.auth',
    # 'django.contrib.contenttypes',
    'django.contrib.sessions',
    # 'django.contrib.sites',
    # 'django.contrib.messages',
    # 'django.contrib.staticfiles',
    # 'django.contrib.admin',
    # 'django.contrib.admindocs',
    'www.custom_tags',
    'www.account',
    'www.question',
    'www.message',
)

AUTHENTICATION_BACKENDS = ('www.middleware.user_backend.AuthBackend',)


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

SESSION_COOKIE_AGE = 60 * 60 * 24 * 10
SESSION_COOKIE_HTTPONLY = True

import logging
logging.basicConfig(format='%(asctime)s %(message)s ---------- %(pathname)s:%(module)s.%(funcName)s Line:%(lineno)d',
                    datefmt='%Y-%m-%d %H:%M:%S', level=logging.WARNING)
