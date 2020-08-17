import requests
import datetime
import json
import pandas as pd


def pm25_to_aqius(pm: float) -> float:
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


def aqi_level(aqi: float) -> str:
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


def get_sensor_data(
        start_date: datetime.datetime,
        end_date: datetime.datetime,
) -> pd.DataFrame:
    interval = end_date - start_date
    start_date = start_date.isoformat('T')
    end_date = end_date.isoformat('T')

    data = requests.get('http://api:8000/sensor_data',
                        json={"end_time": end_date,
                              "start_time": start_date,
                              "columns": ['date', 'p1', 'p2']}
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

    return df


def get_anomaly_data(
        start_date: datetime.datetime,
        end_date: datetime.datetime,
        df: pd.DataFrame,  # sensors data
) -> pd.DataFrame:
    start_date = start_date.isoformat('T')
    end_date = end_date.isoformat('T')
    anom_resp = requests.get('http://api:8000/anomaly',
                             json={"end_time": end_date,
                                   "start_time": start_date}
                             )
    anom_data = json.loads(anom_resp.text)
    anom_df = pd.DataFrame(columns=['p1', 'cluster'])

    for item in anom_data:
        temp = df[item['start_date']:item['end_date']]
        temp['cluster'] = item['cluster']
        anom_df = anom_df.append(temp)
    return anom_df


def get_forecast_data() -> pd.DataFrame:
    data = requests.get('http://api:8000/forecast', json={})
    data = json.loads(data.text)
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df.date, utc=True)
    df['date'] += pd.to_timedelta(df['forward_time'], unit='h')
    df = df[['date', 'p1', 'p2']]
    df = df.set_index('date')
    return df
