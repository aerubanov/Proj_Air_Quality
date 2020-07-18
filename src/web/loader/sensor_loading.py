import requests
import csv
import json
import typing
import numpy as np

from src.web.loader.config import api_url, sensor_file


def read_sensor_id(file: str) -> typing.Set:
    """
    load sensor id
    :param file: file with sensors ID
    :return: set of all sensors id to downloading
    """
    with open(file) as csvf:
        reader = csv.DictReader(csvf)
        id_list = [int(i['sensor_id']) for i in reader]
        return set(id_list)


def load_data(s_id: typing.Set, url=api_url) -> typing.List[typing.Dict]:
    """
    load data using api
    :param s_id: set of sensors ID which will be downloaded
    :param url: api url
    :return: list of dict with sensors_data
    """
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


def filter_average(data: np.array) -> float:
    """average values with outliers removing"""
    q10 = np.quantile(data, q=0.1)
    q90 = np.quantile(data, q=0.9)
    data = data[data < q90]
    data = data[data > q10]
    return data.mean()


def average_data(data: typing.List[typing.Dict]):
    """
    average data fro sensors
    :param data: list of dict with sensors values
    :return: dict with average values
    """
    p1 = [float(i['P1']) for i in data if 'P1' in i]
    p2 = [float(i['P2']) for i in data if 'P2' in i]
    temp = [float(i['temperature']) for i in data if 'temperature' in i]
    hum = [float(i['humidity']) for i in data if 'humidity' in i]
    press = [float(i['pressure']) for i in data if 'pressure' in i]
    return {'p1': filter_average(np.array(p1)),
            'p2': filter_average(np.array(p2)),
            'temp': filter_average(np.array(temp)),
            'press': filter_average(np.array(press)),
            'hum': filter_average(np.array(hum)),
            }


def load_sensors() -> dict:
    """get current average values from sensors"""
    sensor_id = read_sensor_id(sensor_file)
    data = load_data(sensor_id)
    loaded = len(data)
    avg_data = average_data(data)
    return avg_data, loaded
