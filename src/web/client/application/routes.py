from flask import render_template
import altair as alt
import datetime
import requests
import pandas as pd
import json

from src.web.client.application import app


# ------- Pages ----------------------

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/forecast')
def forecast():
    return render_template('forecast.html')

# -------- helper function -----------

def pm25_to_aqius(pm):
    if pm <= 12:
        i_low = 0
        i_high = 50
        c_low = 0
        c_high = 12
    elif 12 < pm <= 35.4:
        i_low = 50
        i_high = 100
        c_low = 12
        c_high = 35.4
    elif 35.4 < pm <= 55.4:
        i_low = 100
        i_high = 150
        c_low = 35.4
        c_high = 55.4
    elif 55.4 < pm <= 150.4:
        i_low = 150
        i_high = 200
        c_low = 55.4
        c_high = 150.4
    elif 150.4 < pm <= 250.4:
        i_low = 200
        i_high = 300
        c_low = 150.4
        c_high = 250.4
    else:
        i_low = 300
        i_high = 500
        c_low = 250.4
        c_high = 500.4
    return (i_high - i_low) / (c_high - c_low) * (pm - c_low) + i_low


def aqi_level(aqi):
    if aqi <= 50:
        return 'good'
    if 50 < aqi <= 100:
        return 'moderate'
    if 100 < aqi <= 150:
        return 'Unhealthy for sens. groups'
    if 150 < aqi <= 200:
        return 'Unhealthy'
    if 200 < aqi <= 300:
        return 'Very Unhealthy'
    if aqi > 300:
        return 'Hazardous'


# -------- Graphs --------------------
WIDTH = 900
HEIGHT = 400

nearest = alt.selection(type='single', nearest=True, on='mouseover',
                        fields=['date'], empty='none')


@app.route('/graph/sensors')
def sensors_graph():
    data = requests.get('http://93.115.20.79:8080/sensor_data',
                        json={"end_time": datetime.datetime.utcnow().isoformat('T'),
                              "start_time": (datetime.datetime.utcnow() - datetime.timedelta(days=3)).isoformat('T')}
                        )
    data = json.loads(data.text)
    df = pd.DataFrame(data)
    df = df[['date', 'p1', 'p2']]
    df['date'] = pd.to_datetime(df.date, utc=True)
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


@app.route('/graph/aqius')
def aqius_graph():
    data = requests.get('http://93.115.20.79:8080/sensor_data',
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
    data = requests.get('http://93.115.20.79:8080/forecast', json={})
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
