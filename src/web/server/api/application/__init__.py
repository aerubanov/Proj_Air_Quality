from flask import Flask
from dotenv import load_dotenv
import os
import environ
from src.web.utils.env_config import AppConfig

load_dotenv('src/web/config.env')

app = Flask(__name__)

config = AppConfig.from_environ(os.environ)

app.config['DATABASE'] = config.server.dbsting
app.config['TEST_DATABASE'] = 'sqlite:///test_db.db'
app.config['DEBUG'] = False

from src.web.server.api.application import routes  # noqa: E402,F401
