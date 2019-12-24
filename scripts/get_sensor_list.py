import requests
import datetime
from bs4 import BeautifulSoup
import csv

from scripts.config import MAX_LAT, MIN_LAT, MAX_LON, MIN_LON, CHECKED_LINKS_FILE, SENSOR_ID_FILE, SERVER_URL

# This script update list of available sensors. Script get all csv files links and check sensor lat and lon
# in range [MIN_LAT, MAX_LAT], [MIN_LON, MAX_LON] respectively. See config.py for that values.


def get_links(for_date, links_file):
    """
    Get all new available links on server
    :param for_date: date for lock up
    :param links_file: file with already checked links
    :return: list of new links
    """
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
        links = [i for i in links if 'indoor' not in i]
    return links


def check_coordinate(lat, lon):
    """check that sensor coordinate is appropriate"""
    return MIN_LAT <= lat <= MAX_LAT and MIN_LON <= lon <= MAX_LON


def check_sensor_pos(links, links_file, sensor_id_file):
    """
    for all new links extract first datastring and check file position
    if true, save id to download data
    :param links: new links for checking
    :param links_file: file with already checked list
    :param sensor_id_file: file with id of appropriate sensor s
    :return: list of new id
    """
    id_list = []
    try:
        fh = open(sensor_id_file, "r")
    except FileNotFoundError:
        fh = open(sensor_id_file, "w")
    fh.close()
    for url in links:
        with open(links_file, 'a') as l_file, requests.Session() as s,\
                open(sensor_id_file, 'a') as s_file:
            try:
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
            except requests.exceptions.ConnectionError as e:
                print(str(e))
    return id_list


if __name__ == '__main__':
    date = datetime.date.today() - datetime.timedelta(days=1)
    ln = get_links(date, CHECKED_LINKS_FILE)
    sensor_list = check_sensor_pos(ln, CHECKED_LINKS_FILE, SENSOR_ID_FILE)
    print(sensor_list)
    with open('last_data_update.txt', 'w') as f:
        f.write(str(date))
