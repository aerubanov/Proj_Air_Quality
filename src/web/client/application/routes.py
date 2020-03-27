from flask import request, render_template
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
    return render_template('test.html')


# -------- Graphs --------------------
WIDTH = 900
HEIGHT = 400


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

    '''
    line = alt.Chart(
        data=df, height=HEIGHT,
        width=WIDTH).mark_line().encode(
        alt.X('date:T', axis=alt.Axis(title='Date')),
        alt.Y('y:Q', axis=alt.Axis(title='Concentration [g/m^3]')),
        color='series:N'
    ).interactive()'''

    nearest = alt.selection(type='single', nearest=True, on='mouseover',
                            fields=['date'], empty='none')

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
                           width=600, height=300, title='Stock History')
    '''
    base = alt.Chart(df.reset_index(), height=HEIGHT,
                     width=WIDTH).encode(x='date')

    return alt.layer(base.mark_line(color='blue').encode(y='p1'),
                     base.mark_line(color='red').encode(y='p2')).interactive().to_json()
    '''
    return conc_chart.to_json()
