from flask import request, abort, g, jsonify
from marshmallow import ValidationError
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import logging.config
import time

from src.web.api.application import app
from src.web.api.application.validation import SensorDataSchema
from src.web.models.model import Base, Sensors
from src.web.logger.logging_config import LOGGING_CONFIG

sensor_data_schema = SensorDataSchema()


def get_logger():
    if 'log' not in g:
        logging.config.dictConfig(LOGGING_CONFIG)
        logger = logging.getLogger('ApiLogger')
        g.log = logger
    return g.log


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
        args = sensor_data_schema.load(request.get_json())
        session = get_db()
        res = session.query(Sensors).filter(args['start_time'] <= Sensors.date)
        res = res.filter(Sensors.date <= args['end_time'])
        res = res.order_by(Sensors.date)
        data = [i.serialize for i in res.all()]
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


@app.before_request
def before_request():
    g.start = time.time()


@app.after_request
def after_request(response):
    if app.config['DEBUG']:
        return response
    resp_time = (time.time() - g.start) * 1000  # время ответа сервера в миллисекндах
    logger = get_logger()
    logger.info(f'path: {request.path} - method: {request.method} - remote: {request.remote_addr} '
                f'- json: {request.json} - status: {response.status} - time: {resp_time}')
    return response
