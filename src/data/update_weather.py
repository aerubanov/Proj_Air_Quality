import datetime
import os
import csv
import requests
import gzip
from bs4 import BeautifulSoup
import re

from src.data.config import WEATHER_DATA_FOLDER, WEATHER_FILE
from src.data.config import WEATHER_URL1, WEATHER_URL2

# DEFAULT_DATE = datetime.date.today() - datetime.timedelta(days=30)
DEFAULT_DATE = datetime.date(2019, 4, 1)


def check_file(fname, data_folder=WEATHER_DATA_FOLDER):
    """
    checking existing weather data
    :param fname: file name for checking
    :param data_folder: path to folder
    :return: (True, last_date) if file with data exist, (False, None) otherwise
    """
    try:
        f = open(os.path.join(data_folder, fname), 'r', encoding="utf-8")
        reader = csv.DictReader(f, delimiter=";")
        try:
            row = next(reversed(list(reader)))
        except StopIteration:
            return False, None
        t = row['Местное время в Москве (центр, Балчуг)']
        t = t.split()[0].split('.')
        day = int(t[0])
        month = int(t[1])
        year = int(t[2])
        dt = datetime.datetime(year, month, day)
        f.close()
        return True, dt.date() + datetime.timedelta(days=1)
    except FileNotFoundError:
        return False, None


def get_link(start_date: datetime.date, end_date: datetime.date):
    date1 = f'{start_date.day}.{start_date.month}.{start_date.year}'
    date2 = f'{end_date.day}.{end_date.month}.{end_date.year}'
    resp = requests.get(WEATHER_URL1)
    php_id = resp.cookies.get_dict()["PHPSESSID"]
    my_url = WEATHER_URL2
    my_header = {}
    my_header["Accept"] = "text/html, */*; q=0.01"
    my_header["Accept-Encoding"] = "gzip, deflate, br"
    my_header["Accept-Language"] = "en-US,en;q=0.5"
    my_header["Connection"] = "keep-alive"
    my_header["Content-Length"] = "98"
    my_header["Content-Type"] = "application/x-www-form-urlencoded"
    my_header["Host"] = "rp5.ru"
    my_header["Origin"] = "https://rp5.ru"
    my_header["Referer"] = "https://rp5.ru/"
    my_header["User-Agent"] = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:71.0) Gecko/20100101 Firefox/71.0"
    my_header["X-Requested-With"] = "XMLHttpRequest"
    my_header["Cookie"] = f"extreme_open=false; ftab=2; tab_synop=2; PHPSESSID={php_id}; i=152492; iru=152492;" \
                          f" ru=%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D0%B0+%28%D1%86%D0%B5%D0%BD%D1%82%D1%80%2C+%D0%91%" \
                          f"D0%B0%D0%BB%D1%87%D1%83%D0%B3%29; last_visited_page=http%3A%2F%2Frp5.ru%2F%D0%9F%D0%BE%D" \
                          f"0%B3%D0%BE%D0%B4%D0%B0_%D0%B2_%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D0%B5_%28%D1%86%D0%B5%D0%" \
                          f"BD%D1%82%D1%80%2C_%D0%91%D0%B0%D0%BB%D1%87%D1%83%D0%B3%29; format=csv; f_enc=utf; lang=ru"
    lang = 'ru'
    my_data = {'wmo_id': '27605', 'a_date1': date1, 'a_date2': date2, 'f_ed3': '9', 'f_ed4': '9',
               'f_ed5': '8', 'f_pe': '1', 'f_pe1': '2', 'lng_id': '2'}
    print(my_data)
    print(my_header)
    response = requests.post(my_url, data=my_data, headers=my_header)
    print(response.text)
    soup = BeautifulSoup(response.text, 'lxml')
    script = soup.find('script')
    link = re.findall(
        """http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+""",
        script.string)[0][:-1]
    link = '/'.join([i for i in link.split('/') if i != '..'])  # remove '/../'
    return link


def download_data(link):
    header = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:71.0) Gecko/20100101 Firefox/71.0',
              'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
              'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
              'Accept-Encoding': 'gzip, deflate',
              'DNT': '1',
              'Connection': 'keep-alive',
              'Upgrade-Insecure-Requests': '1',
              }
    resp = requests.get(url=link, headers=header, stream=True)
    # file = gzip.GzipFile(resp.content, 'rb')
    with open('download_weather_data.gz', 'wb') as f:
        f.write(resp.content)
    with gzip.open('download_weather_data.gz') as g:
        data = g.read().decode('utf-8')
    os.remove('download_weather_data.gz')
    return data


def main(datafile: str):
    file_exist, start_date = check_file(datafile)
    if start_date is None:
        start_date = DEFAULT_DATE
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    if start_date >= yesterday:
        return
    link = get_link(start_date, yesterday)
    data = download_data(link).splitlines()
    data = data[6:]  # skip header
    if not file_exist:
        with open(os.path.join(WEATHER_DATA_FOLDER, datafile), "w") as f:
            f.write(data[0])
    with open(os.path.join(WEATHER_DATA_FOLDER, datafile), 'a', encoding='utf-8') as f:
        for i in reversed(data[1:]):
            f.write(i+'\n')


if __name__ == '__main__':
    main(WEATHER_FILE)
