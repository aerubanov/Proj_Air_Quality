import requests
import numpy as np
import csv
import json
from typing import List, Dict
import datetime
import os

from src.web.server.loader import config
raw_path = 'DATA/raw/mosecom/'
processed_path = 'DATA/processed/'


def load_data():
    """ download json data for PM2.5 and PM10"""
    resp = requests.post(config.mosecomurl,
                         data={'locale': 'ru_RU', 'mapType': 'air', 'element': 'PM2.5'},
                         verify=False)
    data = json.loads(resp.text)
    p1_data = data['able']
    resp = requests.post(config.mosecomurl,
                         data={'locale': 'ru_RU', 'mapType': 'air', 'element': 'PM10'},
                         verify=False)
    data = json.loads(resp.text)
    p2_data = data['able']
    return p1_data, p2_data


def write_raw_data(data: List, data_type: str):
    """write raw data in csv file, separate for each station"""
    date = datetime.datetime.utcnow()
    for item in data:
        name = item['stationId']
        file_name = name+data_type+'.csv'
        path = os.path.join(raw_path, file_name)

        # check if we seen this station before
        if not os.path.exists(path):
            # create file for data
            with open(path, 'w') as file:
                writer = csv.DictWriter(file, fieldnames=['date', 'pdk', 'norma'])
                writer.writeheader()
            # add info about station location in list
            with open(os.path.join(processed_path, 'mosecom_station.csv'), 'a') as file:
                writer = csv.DictWriter(file, fieldnames=['station_name', 'lon', 'lat', 'type'])
                writer.writerow({'station_name': name, 'lon': item['longitude'],
                                 'lat': item['latitude'], 'type': data_type})

        # write data
        with open(path, 'a') as file:
            writer = csv.DictWriter(file, fieldnames=['date', 'pdk', 'norma'])
            row = {'date': date.isoformat('T'), 'pdk': item['pdk'], 'norma': item['norma']}
            writer.writerow(row)


def avarege_data(data: List) -> Dict:
    values = [i['pdk']*i['norma']*1000 for i in data]
    return {
        'p10': np.percentile(values, 10),
        'p25': np.percentile(values, 25),
        'p50': np.percentile(values, 50),
        'p75': np.percentile(values, 75),
        'p90': np.percentile(values, 90),
        'len': len(data)
    }


def write_processed(data_p1, data_p2):
    stat1 = avarege_data(data_p1)
    stat2 = avarege_data(data_p2)
    date = datetime.datetime.utcnow()
    row = {'ts': date, 'mosecom_pm10_count': stat2['len'], 'mosecom_pm10_p10': stat2['p10'],
           'mosecom_pm10_p25': stat2['p25'], 'mosecom_pm10_p50': stat2['p50'], 'mosecom_pm10_p75': stat2['p75'],
           'mosecom_pm10_p90': stat2['p90'], 'mosecom_pm25_count': stat1['len'], 'mosecom_pm25_p10': stat1['p10'],
           'mosecom_pm25_p25': stat1['p25'], 'mosecom_pm25_p50': stat1['p50'], 'mosecom_pm25_p75': stat1['p75'],
           'mosecom_pm25_p90': stat1['p90']}
    with open(os.path.join(processed_path, 'mosecom_moscow_pm.csv'), 'a') as file:
        writer = csv.DictWriter(file, fieldnames=['ts', 'mosecom_pm10_count', 'mosecom_pm10_p10', 'mosecom_pm10_p25',
                                                  'mosecom_pm10_p50', 'mosecom_pm10_p75', 'mosecom_pm10_p90',
                                                  'mosecom_pm25_count', 'mosecom_pm25_p10', 'mosecom_pm25_p25',
                                                  'mosecom_pm25_p50', 'mosecom_pm25_p75', 'mosecom_pm25_p90'],
                                quoting=csv.QUOTE_ALL)
        writer.writerow(row)


def main():
    p1_data, p2_data = load_data()
    write_raw_data(p1_data, 'P1')
    write_raw_data(p2_data, 'P2')
    write_processed(p1_data, p2_data)


if __name__ == '__main__':
    main()
