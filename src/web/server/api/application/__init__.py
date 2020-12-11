from flask import Flask
from src.web.server import config


app = Flask(__name__)

app.config['DATABASE'] = config.dbstring
app.config['DEBUG'] = False

from src.web.server.api.application import routes  # noqa: E402,F401
