from flask import request, abort, g, jsonify
from marshmallow import ValidationError
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import logging.config
import time
from appmetrics import metrics, reporter

from src.web.api.application import app
from src.web.api.application.validation import SensorDataSchema, ForecastRequestSchema, AnomalyRequestSchema
from src.web.models.model import Base, Sensors, Forecast, Anomaly
from src.web.logger.logging_config import LOGGING_CONFIG
from src.web.api.application.metrics_reporter import graphite_reporter

sensor_data_schema = SensorDataSchema()
forecast_schema = ForecastRequestSchema()
anomaly_schema = AnomalyRequestSchema()

meter_200 = metrics.new_meter('status_200')
meter_400 = metrics.new_meter('status_400')
meter_404 = metrics.new_meter('status_404')
reporter.register(graphite_reporter, reporter.fixed_interval_scheduler(5 * 60))  # send metrics every 5 minutes


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


@metrics.with_meter('sensors')
@app.route('/sensor_data', methods=['GET'])
def get_sensor_data():
    try:
        args = sensor_data_schema.load(request.get_json())
    except ValidationError as e:
        abort(400, str(e))
        return
    session = get_db()
    res = session.query(Sensors)
    '''else:
        columns_map = {
            'p1': Sensors.p1,
            'p2': Sensors.p2,
            'pressure': Sensors.pressure,
            'humidity': Sensors.humidity,
            'temperature': Sensors.temperature,
        }
        entities = [columns_map[i] for i in args['columns']]
        res = session.query().with_entities(*entities)'''
    res = res.filter(args['start_time'] <= Sensors.date)
    res = res.filter(Sensors.date <= args['end_time'])
    res = res.order_by(Sensors.date)
    data = [i.serialize for i in res.all()]
    if 'columns' in args:
        data = [{i: item[i] for i in args['columns']} for item in data]
    return jsonify(data)


@metrics.with_meter('forecast')
@app.route('/forecast', methods=['GET'])
def get_forecast():
    try:
        args = forecast_schema.load(request.get_json())
    except ValidationError as e:
        abort(400, str(e))
        return
    session = get_db()
    res = session.query(Forecast)
    if 'start_time' in args:
        res = res.filter(Forecast.date >= args['start_time'])
    if 'end_time' in args:
        res = res.filter(Forecast.date <= args['end_time'])
    res = res.order_by(Forecast.date.desc())
    if 'start_time' not in args and 'end_time' not in args:
        res = res.limit(1)
        date = res.first().date  # get last available datetime for forecast
        res = session.query(Forecast).filter(Forecast.date == date)
    data = [i.serialize for i in res.all()]
    return jsonify(data)


@metrics.with_meter('anomalies')
@app.route('/anomaly', methods=['GET'])
def get_anomaly():
    try:
        args = anomaly_schema.load(request.get_json())
    except ValidationError as e:
        abort(400, str(e))
        return
    session = get_db()
    res = session.query(Anomaly).filter(Anomaly.end_date >= args['start_time']). \
        filter(Anomaly.start_date <= args['end_time'])
    res.order_by(Anomaly.start_date)
    data = [i.serialize for i in res.all()]
    return jsonify(data)


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
    try:
        meter = {response.status_code == 200: meter_200,
                 response.status_code == 400: meter_400,
                 response.status_code == 404: meter_404,
                 }[True]
        meter.notify(1)
    except KeyError:
        pass
    return response
