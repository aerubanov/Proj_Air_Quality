from flask import Flask
try:
    from src.web.config import DATABASE
except ModuleNotFoundError:
    DATABASE = 'postgresql://postgres:postgres@PostgreSQL/pgdb'
app = Flask(__name__)

app.config['DATABASE'] = DATABASE
app.config['TEST_DATABASE'] = 'sqlite:///test_db.db'
app.config['DEBUG'] = False
