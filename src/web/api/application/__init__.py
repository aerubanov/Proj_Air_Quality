from flask import Flask
app = Flask(__name__)

app.config['DATABASE'] = 'postgresql://postgres:postgres@PostgreSQL/pgdb'
app.config['TEST_DATABASE'] = 'sqlite:///test_db.db'
app.config['DEBUG'] = False
