from src.web.loader.config import logs_file

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        },
    },
    'handlers': {
        'log_file_handler': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': logs_file,
            'maxBytes': 1000000,
            'backupCount': 3,
        },
        'api_file_handler': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/api_log.txt',
            'maxBytes': 1000000,
            'backupCount': 3,
        },
        'ml_file_handler': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/ml_log.txt',
            'maxBytes': 1000000,
            'backupCount': 3,
        },
        'db_handler': {
            'level': 'INFO',
            'class': 'src.web.logger.log_handler.LogDBHandler',
        }
    },
    'loggers': {
        'LoaderLogger': {
            'handlers': ['log_file_handler', 'db_handler'],
            'level': 'INFO',
            'propagate': False
        },
        'ApiLogger': {
            'handlers': ['api_file_handler', 'db_handler'],
            'level': 'INFO',
            'propagate': False
        },
        'MLLogger': {
            'handlers': ['ml_file_handler', 'db_handler'],
            'level': 'INFO',
            'propagate': False
        },
    }
}
