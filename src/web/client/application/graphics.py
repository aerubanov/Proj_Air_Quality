import pandas as pd
import matplotlib.pyplot as plt
import mpld3

from src.web.utils.aqi import aqi_level, pm25_to_aqius

WIDTH = 12
HEIGHT = 6


def html_graph(
        sensor_data: pd.DataFrame,
        anomalies_data: pd.DataFrame,
        forecast_data: pd.DataFrame,
        with_forecast=True):
    anom_colors = {0: 'g', 1: 'r', 2: 'b'}

    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(WIDTH, HEIGHT), gridspec_kw={'width_ratios': [2, 1]})

    if not sensor_data.empty:
        axes[0, 0].plot(sensor_data.index.to_pydatetime(), sensor_data.p1.values, label='PM2.5')
        axes[0, 0].plot(sensor_data.index.to_pydatetime(), sensor_data.p2.values, label='PM10')

        aqi_df = sensor_data[['p1']].interpolate()
        aqi_df['aqi'] = aqi_df.p1.apply(pm25_to_aqius)
        aqi_df['aqi'] = aqi_df.aqi.fillna(value=0)
        aqi_df['level'] = aqi_df.aqi.apply(aqi_level)
        axes[1, 0].scatter(
            aqi_df.index.to_pydatetime(),
            aqi_df.aqi.values,
            c=aqi_df.level.values,
            edgecolor='none',
        )
        axes[1, 0].plot(aqi_df.index.to_pydatetime(), aqi_df.aqi.values,)

    if not anomalies_data.empty:
        anomalies_data['cluster'] = anomalies_data.cluster.map(anom_colors)
        axes[0, 0].scatter(
            anomalies_data.index.to_pydatetime(),
            anomalies_data.p1.values,
            c=anomalies_data.cluster.values,
            edgecolor='none',
        )

    if not forecast_data.empty and with_forecast:
        axes[0, 1].plot(
            forecast_data.index.to_pydatetime(),
            forecast_data.p1.values,
            linestyle='--',
            label='PM2.5',
        )
        axes[0, 1].plot(
            forecast_data.index.to_pydatetime(),
            forecast_data.p2.values,
            linestyle='--',
            label='PM10'
        )

        aqi_forecst = forecast_data[['p1']]
        aqi_forecst['aqi'] = aqi_forecst.p1.apply(pm25_to_aqius)
        aqi_forecst['level'] = aqi_forecst.aqi.apply(aqi_level)
        axes[1, 1].scatter(
            aqi_forecst.index.to_pydatetime(),
            aqi_forecst.aqi.values,
            c=aqi_forecst.level.values,
            edgecolor='none',
        )
        axes[1, 1].plot(aqi_forecst.index.to_pydatetime(), aqi_forecst.aqi.values)

    axes[0, 0].legend(loc='best')
    axes[0, 1].legend(loc='best')

    axes[0, 0].title.set_text('Концентрация частиц')
    axes[0, 1].title.set_text('Прогноз концентрации частиц частиц')
    axes[1, 0].title.set_text('AQI US')
    axes[1, 1].title.set_text('Прогноз   AQI US')

    axes[0, 0].set_ylabel('Концентрация г/м^3')
    axes[1, 0].set_ylabel('AQI US индекс')
    axes[1, 0].set_xlabel('Дата')
    axes[1, 1].set_xlabel('Дата')

    axes[0, 0].xaxis.set_ticklabels([])
    axes[0, 1].xaxis.set_ticklabels([])

    if not with_forecast:
        fig.delaxes(axes[0, 1])
        fig.delaxes(axes[1, 1])
    return mpld3.fig_to_html(fig)
