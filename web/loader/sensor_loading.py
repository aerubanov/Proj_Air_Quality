import requests
import csv
import json
import typing

sensor_file = 'DATA/processed/sensors.csv'
api_url = 'https://data.sensor.community/static/v2/data.json'


def read_sensor_id(file: str) -> typing.Set:
    with open(file) as csvf:
        reader = csv.DictReader(csvf)
        id_list = [int(i['sensor_id']) for i in reader]
        return set(id_list)


def load_data(s_id: typing.Set, url=api_url):
    resp = requests.get(url)
    raw_data = json.loads(resp.text)
    data = [i for i in raw_data if i['sensor']['id'] in s_id]
    return data


if __name__ == '__main__':
    sensor_id = read_sensor_id(sensor_file)
    data = load_data(sensor_id)
    print(data)
