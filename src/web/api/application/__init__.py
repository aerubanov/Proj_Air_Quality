from flask import Flask
app = Flask(__name__)

app.config['DATABASE'] = 'postgresql://postgres:postgres@PostgreSQL/pgdb'
