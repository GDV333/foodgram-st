"""
Конфигурация логирования для Django проекта
"""
from pathlib import Path

# Базовая директория проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# Создаем папку для логов, если её нет
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': (
                '[{asctime}] {levelname} {name} {module} '
                '{process:d} {thread:d} {pathname}:{lineno} - {message}'
            ),
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '[{asctime}] {levelname} {name} - {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'error': {
            'format': (
                '[{asctime}] {levelname} {name} {module} '
                '{pathname}:{lineno} - {message}\n{exc_info}'
            ),
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'sql': {
            'format': (
                '[{asctime}] SQL: {message}'
            ),
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'file_debug': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'django_debug.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },
        'file_error': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'django_error.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'error',
            'encoding': 'utf-8',
        },
        'file_sql': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'django_sql.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 3,
            'formatter': 'sql',
            'encoding': 'utf-8',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'console_debug': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file_debug', 'file_error'],
        'level': 'DEBUG',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file_debug', 'file_error'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console_debug', 'file_debug', 'file_error'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.server': {
            'handlers': ['console_debug', 'file_debug'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['file_sql'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.db.backends.schema': {
            'handlers': ['file_sql'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console_debug', 'file_debug', 'file_error'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.utils.autoreload': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        # Логгеры для ваших приложений
        'api': {
            'handlers': ['console_debug', 'file_debug', 'file_error'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'recipes': {
            'handlers': ['console_debug', 'file_debug', 'file_error'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'users': {
            'handlers': ['console_debug', 'file_debug', 'file_error'],
            'level': 'DEBUG',
            'propagate': False,
        },
        # DRF логирование
        'rest_framework': {
            'handlers': ['console_debug', 'file_debug', 'file_error'],
            'level': 'DEBUG',
            'propagate': False,
        },
        # Логирование для отладки
        'foodgram': {
            'handlers': ['console_debug', 'file_debug', 'file_error'],
            'level': 'DEBUG',
            'propagate': False,
        },
        # Логирование для middleware
        'api.middleware': {
            'handlers': ['console_debug', 'file_debug', 'file_error'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
