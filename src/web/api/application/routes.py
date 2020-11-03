import time
import graphyte
from appmetrics import metrics, reporter
from flask import request, abort, g, jsonify
from marshmallow import ValidationError

from src.web.api.application import app
from src.web.api.application.utils import get_db, get_logger
from src.web.api.application.validation import SensorDataSchema, ForecastRequestSchema, AnomalyRequestSchema
from src.web.config import metrics_host
from src.web.models.model import Sensors, Forecast, Anomaly
from src.web.utils.metrics_reporter import GraphyteReporter

sensor_data_schema = SensorDataSchema()
forecast_schema = ForecastRequestSchema()
anomaly_schema = AnomalyRequestSchema()

meter_200 = metrics.new_meter('status_200')
meter_400 = metrics.new_meter('status_400')
meter_404 = metrics.new_meter('status_404')
graphyte.init(metrics_host, prefix='api')
graphite_reporter = GraphyteReporter(graphyte)
reporter.register(graphite_reporter, reporter.fixed_interval_scheduler(5 * 60))  # send metrics every 5 minutes


@app.route('/sensor_data', methods=['GET'])
@metrics.with_meter('sensors')
def get_sensor_data():
    try:
        args = sensor_data_schema.load(request.get_json())
    except ValidationError as e:
        abort(400, str(e))
        return
    session = get_db(app)
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


@app.route('/forecast', methods=['GET'])
@metrics.with_meter('forecast')
def get_forecast():
    try:
        args = forecast_schema.load(request.get_json())
    except ValidationError as e:
        abort(400, str(e))
        return
    session = get_db(app)
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


@app.route('/anomaly', methods=['GET'])
@metrics.with_meter('anomalies')
def get_anomaly():
    try:
        args = anomaly_schema.load(request.get_json())
    except ValidationError as e:
        abort(400, str(e))
        return
    session = get_db(app)
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
    resp_time = (time.time() - g.start) * 1000  # response time in milliseconds
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
