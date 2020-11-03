import csv
import datetime
import json

import requests
from bs4 import BeautifulSoup

from src.web.loader.config import TRAFFIC_MAP_URL, TRAFFIC_LEVEL_URL

DATA_PATH = 'DATA/processed/trafic_level.csv'
REQUEST_HEADER = {
    'Host': 'yandex.ru',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:76.0) Gecko/20100101 Firefox/76.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0',
    'TE': 'Trailers'
}


class TrafficLoader:

    def __init__(self):
        self.__cookies = {}
        self.__sess_id = ''
        self.__token = ''
        self.__level = -1

    def __prepare_api_call(self, map_url: str):
        resp = requests.get(map_url, headers=REQUEST_HEADER)
        soup = BeautifulSoup(resp.text, 'lxml')
        script = soup.find("script", {"class": "config-view"})

        if not len(script.contents):
            return

        conf = json.loads(script.contents[0].strip())

        self.__sess_id = conf['counters']['analytics']['sessionId']
        self.__token = conf['csrfToken']
        self.__cookies = resp.cookies

    def __load_traffic_level(self, level_url: str):
        param = {'ajax': '1', 'csrfToken': self.__token, 'ids[0]': '213', 'ids[1]': '1',
                 'sessionId': self.__sess_id, 'ids[0': '213'}
        resp = requests.get(level_url, cookies=self.__cookies, headers=REQUEST_HEADER, params=param)

        if resp.status_code == 200:
            data = resp.json()
            self.__level = data['data']['level']

    def __write_traffic_level(self) -> bool:
        if self.__level == -1:
            return False

        date = datetime.datetime.utcnow()

        with open(DATA_PATH, 'a') as file:
            writer = csv.DictWriter(file, fieldnames=['date', 'traffic_level'])
            writer.writerow({'date': date, 'traffic_level': self.__level})

        return True

    def process_traffic_level(self):
        self.__prepare_api_call(TRAFFIC_MAP_URL)
        self.__load_traffic_level(TRAFFIC_LEVEL_URL)
        is_success = self.__write_traffic_level()
        return is_success
