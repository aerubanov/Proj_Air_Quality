from flask import request, abort, g, jsonify
from marshmallow import ValidationError
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from src.web.api.application import app
from src.web.api.application.validation import SensorDataSchema
from src.web.models.model import Base, Sensors

sensor_data_schema = SensorDataSchema()


def create_db():
    engine = create_engine(app.config['DATABASE'])
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def get_db():
    if 'db' not in g:
        session = create_db()
        g.db = session
    return g.db


@app.route('/sensor_data', methods=['GET'])
def get_sensor_data():
    try:
        args = sensor_data_schema.loads(request.args)
        session = get_db()
        res = session.query(Sensors).filter(args['start_time'] <= Sensors.date <= args['end_time']).all()
        res = res.order_by(Sensors.date)
        data = [i.serialize for i in res]
        return jsonify(data)
    except ValidationError as e:
        abort(400, str(e))


@app.teardown_appcontext
def teardown_db(args):
    db = g.pop('db', None)
    log_db = g.pop('log_session', None)
    if log_db is not None:
        log_db.close()
    if db is not None:
        db.close()
