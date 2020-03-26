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

    line = alt.Chart(
        data=df, height=HEIGHT,
        width=WIDTH).mark_line().encode(
        alt.X('date:T', axis=alt.Axis(title='Date')),
        alt.Y('y:Q', axis=alt.Axis(title='Concentration [g/m^3]')),
        color='series:N'
    ).interactive()

    return line.to_json()
