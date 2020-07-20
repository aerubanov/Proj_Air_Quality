from flask import render_template, request, session, url_for, g
import altair as alt
import datetime
import requests
import pandas as pd
import json
from flask_wtf import FlaskForm
from wtforms.fields.html5 import DateField
from wtforms.fields import SubmitField
import logging.config
import time

from src.web.client.application import app
from src.web.client.application.helper_functions import pm25_to_aqius, aqi_level
from src.web.logger.logging_config import LOGGING_CONFIG


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
    resp_time = (time.time() - g.start) * 1000  # время ответа сервера в миллисекндах
    logger = get_logger()
    logger.info(f'path: {request.path} - method: {request.method} - remote: {request.remote_addr} '
                f'- json: {request.json} - status: {response.status} - time: {resp_time}')
    return response

# ------- Pages ----------------------


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/forecast')
def forecast():
    return render_template('forecast.html')


@app.route('/history', methods=['POST', 'GET'])
def history():
    form = DateForm()
    if request.method == 'POST':
        session['start_date'] = datetime.datetime.combine(form.start_date.data,
                                                          datetime.datetime.min.time()).isoformat()
        session['end_date'] = datetime.datetime.combine(form.end_date.data,
                                                        datetime.datetime.min.time()).isoformat()
    return render_template('history.html', form=form)


@app.route('/anomalies', methods=['POST', 'GET'])
def anomalies():
    form = DateForm()
    if request.method == 'POST':
        session['start_date'] = datetime.datetime.combine(form.start_date.data,
                                                          datetime.datetime.min.time()).isoformat()
        session['end_date'] = datetime.datetime.combine(form.end_date.data,
                                                        datetime.datetime.min.time()).isoformat()
    return render_template('anomalies.html', form=form)


# -------- Graphs --------------------
WIDTH = 900
HEIGHT = 400

nearest = alt.selection(type='single', nearest=True, on='mouseover',
                        fields=['date'], empty='none')


@app.route('/graph/sensors')
def sensors_graph():
    if 'start_date' in session:
        start_date = datetime.datetime.fromisoformat(session['start_date'])
        session.pop('start_date')
    else:
        start_date = (datetime.datetime.utcnow() - datetime.timedelta(days=3))

    if "end_date" in session:
        end_date = datetime.datetime.fromisoformat(session['end_date'])
        session.pop('end_date')
    else:
        end_date = datetime.datetime.utcnow()
    interval = end_date - start_date
    start_date = start_date.isoformat('T')
    end_date = end_date.isoformat('T')

    data = requests.get(app.config['API_URL'] + 'sensor_data',
                        json={"end_time": end_date,
                              "start_time": start_date}
                        )
    data = json.loads(data.text)
    df = pd.DataFrame(data)
    df = df[['date', 'p1', 'p2']]
    df['date'] = pd.to_datetime(df.date, utc=True)
    df = df.set_index('date')

    if interval > datetime.timedelta(days=5):
        df = df.resample('0.5H').mean()
    if interval > datetime.timedelta(days=15):
        df = df.resample('1H').mean()

    df = df.reset_index().melt('date', var_name='series', value_name='y')

    line = alt.Chart().mark_line(interpolate='basis').encode(
        alt.X('date:T', axis=alt.Axis(title='Date')),
        alt.Y('y:Q', axis=alt.Axis(title='Concentration [g/m^3]')),
        color='series:N'
    )

    selectors = alt.Chart().mark_point().encode(
        x='date:T',
        opacity=alt.value(0),
    ).add_selection(
        nearest
    )

    points = line.mark_point().encode(
        opacity=alt.condition(nearest, alt.value(1), alt.value(0))
    )

    text = line.mark_text(align='left', dx=5, dy=-5).encode(
        text=alt.condition(nearest, 'y:Q', alt.value(' '))
    )

    rules = alt.Chart().mark_rule(color='gray').encode(
        x='date:T',
    ).transform_filter(
        nearest
    )

    conc_chart = alt.layer(line, selectors, points, rules, text,
                           data=df,
                           width=WIDTH, height=HEIGHT)
    return conc_chart.to_json()


@app.route('/graph/aqius')
def aqius_graph():
    data = requests.get(app.config['API_URL'] + 'sensor_data',
                        json={"end_time": datetime.datetime.utcnow().isoformat('T'),
                              "start_time": (datetime.datetime.utcnow() - datetime.timedelta(days=3)).isoformat('T')}
                        )
    data = json.loads(data.text)
    df = pd.DataFrame(data)
    df = df[['date', 'p1']]
    df['date'] = pd.to_datetime(df.date, utc=True)
    df['aqi'] = df.p1.apply(pm25_to_aqius)
    df['level'] = df.aqi.apply(aqi_level)

    domain = ['good', 'moderate', 'Unhealthy for sens. groups', 'Unhealthy', 'Very Unhealthy', 'Hazardous']
    range_ = ['green', '#e6ed13', 'orange', 'red', 'purple', 'brown']

    line = alt.Chart(
        data=df, height=HEIGHT,
        width=WIDTH).mark_bar().encode(
        x=alt.X('date:T', axis=alt.Axis(title='Date')),
        y=alt.Y('aqi:Q', axis=alt.Axis(title='AQI US index')),
        color=alt.Color('level', scale=alt.Scale(domain=domain, range=range_))
    ).interactive()
    return line.to_json()


@app.route('/graph/forecast')
def forecast_graph():
    data = requests.get(app.config['API_URL'] + 'forecast', json={})
    data = json.loads(data.text)
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df.date, utc=True)
    df['date'] += pd.to_timedelta(df['forward_time'], unit='h')
    df = df[['date', 'p1', 'p2']]
    df = df.set_index('date')
    df = df.reset_index().melt('date', var_name='series', value_name='y')

    line = alt.Chart().mark_line(interpolate='basis').encode(
        alt.X('date:T', axis=alt.Axis(title='Date')),
        alt.Y('y:Q', axis=alt.Axis(title='Concentration [g/m^3]')),
        color='series:N'
    )

    selectors = alt.Chart().mark_point().encode(
        x='date:T',
        opacity=alt.value(0),
    ).add_selection(
        nearest
    )

    points = line.mark_point().encode(
        opacity=alt.condition(nearest, alt.value(1), alt.value(0))
    )

    text = line.mark_text(align='left', dx=5, dy=-5).encode(
        text=alt.condition(nearest, 'y:Q', alt.value(' '))
    )

    rules = alt.Chart().mark_rule(color='gray').encode(
        x='date:T',
    ).transform_filter(
        nearest
    )

    conc_chart = alt.layer(line, selectors, points, rules, text,
                           data=df,
                           width=WIDTH, height=HEIGHT)
    return conc_chart.to_json()


@app.route('/graph/anomalies')
def anomalies_graph():
    if 'start_date' in session:
        start_date = datetime.datetime.fromisoformat(session['start_date'])
        session.pop('start_date')
    else:
        start_date = (datetime.datetime.utcnow() - datetime.timedelta(days=3))

    if "end_date" in session:
        end_date = datetime.datetime.fromisoformat(session['end_date'])
        session.pop('end_date')
    else:
        end_date = datetime.datetime.utcnow()
    interval = end_date - start_date
    start_date = start_date.isoformat('T')
    end_date = end_date.isoformat('T')

    data = requests.get(app.config['API_URL'] + 'sensor_data',
                        json={"end_time": end_date,
                              "start_time": start_date}
                        )
    data = json.loads(data.text)
    df = pd.DataFrame(data)
    df = df[['date', 'p1']]
    df['date'] = pd.to_datetime(df.date, utc=True)
    df = df.set_index('date')

    if interval > datetime.timedelta(days=5):
        df = df.resample('0.5H').mean()
    if interval > datetime.timedelta(days=15):
        df = df.resample('1H').mean()

    anom_resp = requests.get(app.config['API_URL'] + 'anomaly',
                             json={"end_time": end_date,
                                   "start_time": start_date}
                             )
    anom_data = json.loads(anom_resp.text)
    anom_df = pd.DataFrame(columns=['p1', 'cluster'])

    for item in anom_data:
        temp = df[item['start_date']:item['end_date']]
        temp['cluster'] = item['cluster']
        anom_df = anom_df.append(temp)

    df = df.reset_index()
    anom_df = anom_df.reset_index()

    line = alt.Chart(data=df).mark_line(interpolate='basis').encode(
        x=alt.X('date:T', axis=alt.Axis(title='Date')),
        y=alt.Y('p1:Q', axis=alt.Axis(title='Concentration [g/m^3]'))

    ).interactive()

    range_ = ['red', 'green', 'blue', '#7D3C98']
    domain = [0, 1, 2, 3]

    bar = alt.Chart(data=anom_df).mark_bar().encode(
        x=alt.X('index:T'),
        y=alt.Y('p1:Q'),
        color=alt.Color('cluster:N', scale=alt.Scale(domain=domain, range=range_))
    ).interactive()

    chart = alt.layer(line, bar, width=WIDTH, height=HEIGHT)
    return chart.to_json()
