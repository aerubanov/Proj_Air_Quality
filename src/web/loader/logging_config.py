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
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': logs_file,
            'maxBytes': 100000,
            'backupCount': 3,
        },
    },
    'loggers': {
        'LoaderLogger': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': False
        },
    }
}
