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
        'file_handler': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': logs_file,
            'maxBytes': 100000,
            'backupCount': 3,
        },
        'db_handler': {
            'level': 'INFO',
            'class': 'src.web.loader.log_handler.LogDBHandler',
        }
    },
    'loggers': {
        'LoaderLogger': {
            'handlers': ['file_handler', 'db_handler'],
            'level': 'INFO',
            'propagate': False
        },
    }
}
