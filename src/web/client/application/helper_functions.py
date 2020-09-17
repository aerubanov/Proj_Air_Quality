import requests
import datetime
import json
import pandas as pd
from typing import Optional


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
    df = df.set_index(df.index.tz_convert('Europe/Moscow'))

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


def get_forecast_data() -> Optional[pd.DataFrame]:
    data = requests.get('http://api:8000/forecast', json={})
    try:
        data = json.loads(data.text)
    except json.JSONDecodeError:
        return None
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df.date, utc=True)
    df['date'] += pd.to_timedelta(df['forward_time'], unit='h')
    df = df[['date', 'p1', 'p2']]
    df = df.set_index('date')
    df = df.set_index(df.index.tz_convert('Europe/Moscow'))
    return df
