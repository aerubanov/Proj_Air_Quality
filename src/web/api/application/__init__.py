from flask import Flask
from src.web.config import DATABASE
app = Flask(__name__)

app.config['DATABASE'] = 'DATABASE'
app.config['TEST_DATABASE'] = 'sqlite:///test_db.db'
app.config['DEBUG'] = False
