from flask import Flask


app = Flask(__name__, static_url_path='/static')

app.config['SECRET_KEY'] = 'secret'
app.config['API_URL'] = 'http://api:8000/'

from src.web.client.application import routes  # noqa: E402,F401
