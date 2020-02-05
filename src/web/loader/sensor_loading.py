import requests
import csv
import json
import typing
import numpy as np

from src.web.loader.config import api_url


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
