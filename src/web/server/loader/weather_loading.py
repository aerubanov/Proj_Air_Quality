import requests
from bs4 import BeautifulSoup
import datetime
import typing
import pytz

from src.web.server.loader.config import weather_url


def parse_page(url: str) -> typing.List['BeautifulSoup.Tag']:
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'lxml')

    table = soup.find("table", {"id": "forecastTable_1"})
    rows = table.find_all('tr')
    return rows


def get_times(row: 'BeautifulSoup.Tag') -> typing.List[datetime.datetime]:
    cells = row.find_all('td')
    result = list()
    days = 0
    for i in cells[1:]:
        h = int(i.text)
        dt = datetime.datetime.combine(datetime.date.today()+datetime.timedelta(days=1*days), datetime.time(h),
                                       tzinfo=pytz.timezone('Europe/Moscow'))
        dt = dt.astimezone(pytz.utc)
        result.append(dt)
        if h == 23:
            days += 1  # start next day
    return result


def get_prec(row: 'BeautifulSoup.Tag') -> typing.List[str]:
    result = []
    for i in row.find_all('div', onmouseover=True):
        result.append(i['onmouseover'].split(',')[1])
    result = result[::2]  # list consist results for both metric and imperial unit systems. Skip imperial.
    return result


def get_row_val(row: 'BeautifulSoup.Tag') -> typing.List[float]:
    cells = row.find_all('td')
    result = [float(i.text.split()[0]) for i in cells[1:]]
    return result


def get_row_text(row: 'BeautifulSoup.Tag') -> typing.List[float]:
    cells = row.find_all('td')
    result = [i.text.split()[0] for i in cells[1:]]
    return result


def get_rows_numb(rows):
    rows_nomb = {}
    i = 0
    for r in rows:
        t = r.find('td').text
        if 'Местное время' in t:
            rows_nomb['time_row'] = i
        if 'Осадки, мм' in t:
            rows_nomb['prec_row'] = i
        if 'Температура' in t:
            rows_nomb['temp_row'] = i
        if 'Давление' in t:
            rows_nomb['press_row'] = i
        if 'Ветер' in t:
            rows_nomb['wind_speed_row'] = i
        if 'направление' in t:
            rows_nomb['wind_dir_row'] = i
        if 'Влажность' in t:
            rows_nomb['hum_row'] = i
        i += 1
    return rows_nomb


def parse_weather():
    rows = parse_page(weather_url)
    r = get_rows_numb(rows)
    times = get_times(rows[r['time_row']])
    prec = get_prec(rows[r['prec_row']])
    temp = get_row_val(rows[r['temp_row']])
    press = get_row_val(rows[r['press_row']])
    wind_speed = get_row_val(rows[r['wind_speed_row']])
    wind_dir = get_row_text(rows[r['wind_dir_row']])
    hum = get_row_val(rows[r['hum_row']])
    return {
        'date': times,
        'prec': prec,
        'temp': temp,
        'pressure': press,
        'wind_speed': wind_speed,
        'wind_dir': wind_dir,
        'humidity': hum,
    }


if __name__ == '__main__':
    res = parse_weather()
    for i in range(len(res['date'])):
        print(f"{res['date'][i]} {res['prec'][i]} {res['temp'][i]} {res['pressure'][i]} {res['wind_speed'][i]} "
              f"{res['wind_dir'][i]} {res['humidity'][i]}")