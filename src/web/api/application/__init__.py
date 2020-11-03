from flask import Flask

app = Flask(__name__)

try:
    from src.web.config import DATABASE
except ModuleNotFoundError:
    DATABASE = 'postgresql://postgres:postgres@PostgreSQL/pgdb'

app.config['DATABASE'] = DATABASE
app.config['TEST_DATABASE'] = 'sqlite:///test_db.db'
app.config['DEBUG'] = False

from src.web.api.application import routes  # noqa: E402,F401
