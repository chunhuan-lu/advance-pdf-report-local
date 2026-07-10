"""
Advance Report Studio — 本地优先的安全合规报告生成工具。

默认本地模式：照片 / PDF / 数据库全部存在 local_store/ 下。
设置环境变量 STORAGE_MODE=s3（并配置 AWS 凭证、安装 boto3）可切换到 S3 存储。
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'local-only-tool-not-a-secret')

DEBUG = True

ALLOWED_HOSTS = ['*']  # 允许局域网内手机访问

INSTALLED_APPS = [
    'django.contrib.staticfiles',
    'rest_framework',
    'reports',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': False,
        'OPTIONS': {'context_processors': []},
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

LOCAL_STORE = BASE_DIR / 'local_store'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': LOCAL_STORE / 'db.sqlite3',
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Australia/Melbourne'
USE_I18N = False
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'statics']

MEDIA_URL = '/media/'
MEDIA_ROOT = LOCAL_STORE / 'media'

# local: 照片和 PDF 存 MEDIA_ROOT，前端拿到 /media/... 相对链接
# s3:    沿用 boto3 上传并返回预签名链接（需要 AWS 凭证）
STORAGE_MODE = os.environ.get('STORAGE_MODE', 'local')

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.AllowAny'],
    'UNAUTHENTICATED_USER': None,
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

DATA_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024  # 允许大照片上传
FILE_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024
