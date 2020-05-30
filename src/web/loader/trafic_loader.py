from bs4 import BeautifulSoup
import json
import requests
import datetime
import csv

from src.web.loader.config import trafic_map_url, trafic_level_url

DATA_PATH = 'DATA/processed/trafic_level.csv'


def get_traffic_ball(map_url, level_url):
    header = {'Host': 'yandex.ru',
              'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:76.0) Gecko/20100101 Firefox/76.0',
              'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
              'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
              'Accept-Encoding': 'gzip, deflate, br',
              'DNT': '1',
              'Connection': 'keep-alive',
              'Upgrade-Insecure-Requests': '1',
              'Cache-Control': 'max-age=0',
              'TE': 'Trailers',
              }
    resp = requests.get(map_url, headers=header)

    soup = BeautifulSoup(resp.text, 'lxml')
    content = soup.find("script", {"class": "config-view"})
    print(content.text)
    conf = json.loads(content.text)
    sess_id = conf['counters']['analytics']['sessionId']
    token = conf['csrfToken']

    param = {'ajax': '1', 'csrfToken': token, 'ids[0]': '213', 'ids[1]': '1', 'sessionId': sess_id, 'ids[0': '213'}
    resp = requests.get(level_url, cookies=resp.cookies,
                        headers=header, params=param)
    data = json.loads(resp.text)
    return data['data']['level']


def load_traffic_level():
    level = get_traffic_ball(trafic_map_url, trafic_level_url)
    date = datetime.datetime.utcnow()
    with open(DATA_PATH, 'a') as file:
        writer = csv.DictWriter(file, fieldnames=['date', 'traffic_level'])
        writer.writerow({'date': date, 'traffic_level': level})


if __name__ == "__main__":
    load_traffic_level()
