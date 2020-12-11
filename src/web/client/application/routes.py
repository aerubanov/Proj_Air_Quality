import datetime
import logging.config
import time

import graphyte
from appmetrics import metrics, reporter
from flask import render_template, request, session, g
from flask_wtf import FlaskForm
from wtforms.fields import SubmitField
from wtforms.fields.html5 import DateField

from src.web.client.application import app
from src.web.client.application.graphics import html_graph
from src.web.client.application.helper_functions import get_sensor_data, get_anomaly_data, get_forecast_data
from src.web import config
from src.web.client.logging_config import LOGGING_CONFIG
from src.web.utils.metrics_reporter import GraphyteReporter

meter_200 = metrics.new_meter('client_status_200')
meter_400 = metrics.new_meter('client_status_400')
meter_404 = metrics.new_meter('client_status_404')
graphyte.init(config.metrichost, prefix='client')
graphite_reporter = GraphyteReporter(graphyte)
reporter.register(graphite_reporter, reporter.fixed_interval_scheduler(5 * 60))  # send metrics every 5 minutes


class DateForm(FlaskForm):
    start_date = DateField('начальная дата', format='%Y-%m-%d')
    end_date = DateField('конечная дата', format='%Y-%m-%d')
    submit = SubmitField('Submit')


def get_logger():
    if 'log' not in g:
        logging.config.dictConfig(LOGGING_CONFIG)
        logger = logging.getLogger('ClientLogger')
        g.log = logger
    return g.log


@app.before_request
def before_request():
    g.start = time.time()


@app.after_request
def after_request(response):
    if app.config['DEBUG']:
        return response
    resp_time = (time.time() - g.start) * 1000  # время ответа сервера в миллисекундах
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


# ------- Pages ----------------------


@app.route('/', methods=['POST', 'GET'])
@app.route('/index', methods=['POST', 'GET'])
@metrics.with_meter('index')
def index():
    form = DateForm()
    if request.method == 'POST':
        if form.start_date.data is not None:
            session['start_date'] = datetime.datetime.combine(form.start_date.data,
                                                              datetime.datetime.min.time()).isoformat()
        if form.end_date.data is not None:
            session['end_date'] = datetime.datetime.combine(form.end_date.data,
                                                            datetime.datetime.min.time()).isoformat()
    return render_template('index.html', form=form)


# -------- Graphs --------------------

@app.route('/graph')
def sensors_graph():
    with_forecast = True
    if 'start_date' in session:
        start_date = datetime.datetime.fromisoformat(session['start_date'])
        session.pop('start_date')
        with_forecast = False
    else:
        start_date = (datetime.datetime.utcnow() - datetime.timedelta(days=3))

    if "end_date" in session:
        end_date = datetime.datetime.fromisoformat(session['end_date'])
        session.pop('end_date')
        with_forecast = False
    else:
        end_date = datetime.datetime.utcnow()

    sensor_df = get_sensor_data(start_date, end_date)
    anom_df = get_anomaly_data(start_date, end_date, sensor_df)
    forecast_df = get_forecast_data()

    graph = html_graph(sensor_df, anom_df, forecast_df, with_forecast=with_forecast)

    return graph
