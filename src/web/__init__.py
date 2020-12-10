from dotenv import load_dotenv
import os
from src.web.utils.env_config import AppConfig

load_dotenv('src/web/config.env')
config = AppConfig.from_environ(os.environ)
