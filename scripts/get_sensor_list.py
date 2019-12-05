import requests
import datetime
from bs4 import BeautifulSoup
import csv

from scripts.config import MAX_LAT, MIN_LAT, MAX_LON, MIN_LON, CHECKED_LINKS_FILE, SENSOR_ID_FILE, SERVER_URL


def get_links(for_date, links_file):
    try:
        fh = open(links_file, "r")
    except FileNotFoundError:
        fh = open(links_file, "w")
    fh.close()
    with open(links_file, 'r') as links_file:
        checked_links = links_file.read().splitlines()
        checked_links = [i[10:] for i in checked_links]
        url = SERVER_URL + str(for_date) + '/'
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, 'lxml')
        links = [link.get('href') for link in soup.find_all('a')]
        links = [i for i in links if str(for_date) in i and i[10:] not in checked_links]
        links = [url+i for i in links]
    return links


def check_coordinate(lat, lon):
    return MIN_LAT <= lat <= MAX_LAT and MIN_LON <= lon <= MAX_LON


def check_sensor_pos(links, links_file, sensor_id_file):
    id_list = []
    try:
        fh = open(sensor_id_file, "r")
    except FileNotFoundError:
        fh = open(sensor_id_file, "w")
    fh.close()
    for url in links:
        with open(links_file, 'a') as l_file, requests.Session() as s,\
                open(sensor_id_file, 'a') as s_file:
            download = s.get(url)
            decoded_content = download.content.decode('utf-8')
            cr = csv.DictReader(decoded_content.splitlines(), delimiter=';')
            row = next(cr)
            print(row)
            try:
                lat = float(row['lat'])
                lon = float(row['lon'])
                fname = url.split("/")[-1]
                l_file.write(fname+'\n')
                if check_coordinate(lat, lon):
                    id_list.append(fname[10:])
                    s_file.write(fname[10:]+'\n')
                    print(fname[10:])
            except ValueError:
                pass
    return id_list


if __name__ == '__main__':
    date = datetime.datetime(2019, 12, 4)
    ln = get_links(date.date(), CHECKED_LINKS_FILE)
    sensor_list = check_sensor_pos(ln, CHECKED_LINKS_FILE, SENSOR_ID_FILE)
    print(sensor_list)
