import os
from src.web.utils.env_config import AppConfig

config = AppConfig.from_environ(os.environ).bot
