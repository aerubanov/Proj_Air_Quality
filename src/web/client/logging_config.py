client_logs_file = 'logs/client_log.txt'

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        },
    },
    'handlers': {
        'client_file_handler': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': client_logs_file,
            'maxBytes': 1000000,
            'backupCount': 3,
        },
    },
    'loggers': {
        'ClientLogger': {
            'handlers': ['client_file_handler'],
            'level': 'INFO',
            'propagate': False
        },
    }
}
