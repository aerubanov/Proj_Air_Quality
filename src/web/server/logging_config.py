loader_logs_file = 'logs/loader_log.txt'
api_logs_file = 'logs/api_log.txt'
ml_logs_file = 'logs/ml_log.txt'

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        },
    },
    'handlers': {
        'loader_file_handler': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': loader_logs_file,
            'maxBytes': 1000000,
            'backupCount': 3,
        },
        'api_file_handler': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': api_logs_file,
            'maxBytes': 1000000,
            'backupCount': 3,
        },
        'ml_file_handler': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': ml_logs_file,
            'maxBytes': 1000000,
            'backupCount': 3,
        },
    },
    'loggers': {
        'LoaderLogger': {
            'handlers': ['loader_file_handler'],
            'level': 'INFO',
            'propagate': False
        },
        'ApiLogger': {
            'handlers': ['api_file_handler'],
            'level': 'INFO',
            'propagate': False
        },
        'MLLogger': {
            'handlers': ['ml_file_handler'],
            'level': 'INFO',
            'propagate': False
        },
    }
}
