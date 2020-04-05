from flask import Flask
app = Flask(__name__, static_url_path='/static')

app.config['SECRET_KEY'] = 'secret'
# app.config['API_URL'] = 'http://api:8000/'
app.config['API_URL'] = 'http://93.115.20.79:8000/'
