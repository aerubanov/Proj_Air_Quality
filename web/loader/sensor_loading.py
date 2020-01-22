import requests
import csv
import json
import typing
import schedule
import time
import numpy as np

sensor_file = 'DATA/processed/sensors.csv'  # file with information about sensors to data downloading
api_url = 'https://data.sensor.community/static/v2/data.json'
time_interval = 0.5  # interval for api requests in minutes


def read_sensor_id(file: str) -> typing.Set:
    with open(file) as csvf:
        reader = csv.DictReader(csvf)
        id_list = [int(i['sensor_id']) for i in reader]
        return set(id_list)


def load_data(s_id: typing.Set, url=api_url) -> typing.List[typing.Dict]:
    resp = requests.get(url)
    raw_data = json.loads(resp.text)
    data = [i for i in raw_data if i['sensor']['id'] in s_id and i['location']['indoor'] != 1]
    result = []
    for i in data:
        d = dict()
        d['id'] = i['sensor']['id']
        for j in i['sensordatavalues']:
            d[j['value_type']] = j['value']
        result.append(d)
    return result


def average_data(data: typing.List[typing.Dict]):
    p1 = [float(i['P1']) for i in data if 'P1' in i]
    p2 = [float(i['P2']) for i in data if 'P2' in i]
    temp = [float(i['temperature']) for i in data if 'temperature' in i]
    hum = [float(i['humidity']) for i in data if 'humidity' in i]
    press = [float(i['pressure']) for i in data if 'pressure' in i]
    return {'p1': np.mean(p1),
            'p2': np.mean(p2),
            'temp': np.mean(temp),
            'press': np.mean(press),
            'hum': np.mean(hum),
            }


def run_task():
    sensor_id = read_sensor_id(sensor_file)
    data = load_data(sensor_id)
    print(avarage_data(data))


def main():
    schedule.every(time_interval).minutes.do(run_task)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    main()
