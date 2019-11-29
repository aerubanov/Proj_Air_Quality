import requests
import datetime
from bs4 import BeautifulSoup
import csv

MIN_LAT = 55.26
MAX_LAT = 56.47
MIN_LON = 36.82
MAX_LON = 38.40

SERVER_URL = 'http://archive.luftdaten.info/'


def get_links(for_date):
    url = SERVER_URL + str(for_date) + '/'
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'lxml')
    links = [link.get('href') for link in soup.find_all('a')]
    links = [i for i in links if str(for_date) in i]
    links = [url+i for i in links]
    return links


def check_sensor_pos(links):
    id_list = []
    for url in links:
        with requests.Session() as s:
            download = s.get(url)
            decoded_content = download.content.decode('utf-8')
            cr = csv.DictReader(decoded_content.splitlines(), delimiter=';')
            row = next(cr)
            print(row)

            sensor_id = row['sensor_id']
            lat = float(row['lat'])
            lon = float(row['lon'])

            if MIN_LAT <= lat <= MAX_LAT and MIN_LON <= lon <= MAX_LAT:
                id_list.append(sensor_id)
    return id_list


if __name__ == '__main__':
    date = datetime.datetime(2019, 11, 27)
    ln = get_links(date.date())
    print(check_sensor_pos(ln))
