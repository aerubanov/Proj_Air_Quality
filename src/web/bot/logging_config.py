bot_logs_file = 'logs/bot_log.txt'

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        },
    },
    'handlers': {
        'bot_file_handler': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': bot_logs_file,
            'maxBytes': 1000000,
            'backupCount': 3,
        },
    },
    'loggers': {
        'BotLogger': {
            'handlers': ['bot_file_handler'],
            'level': 'INFO',
            'propagate': False
        }
    }
}
