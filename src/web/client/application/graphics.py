import altair as alt
import pandas as pd

from src.web.client.application.helper_functions import aqi_level, pm25_to_aqius

WIDTH = 900
HEIGHT = 400
nearest = alt.selection(type='single', nearest=True, on='mouseover',
                        fields=['date'], empty='none')


def aqius_graph(df: pd.DataFrame):
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
    return line


def senors_graph(df: pd.DataFrame):
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
    return conc_chart


def anomalies_graph(anom_df: pd.DataFrame):
    range_ = ['green', 'red', 'blue']
    domain = [0, 1, 2]

    anom_df = anom_df.reset_index()

    bar = alt.Chart(data=anom_df).mark_bar().encode(
        x=alt.X('index:T'),
        y=alt.Y('p1:Q'),
        color=alt.Color('cluster:N', scale=alt.Scale(domain=domain, range=range_))
    ).interactive()

    return bar
