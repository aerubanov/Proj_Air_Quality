import requests
from bs4 import BeautifulSoup
import datetime
import typing

weather_url = 'https://rp5.ru/%D0%9F%D0%BE%D0%B3%D0%BE%D0%B4%D0%B0_%D0%B2_%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D0%B5' \
      '_(%D1%86%D0%B5%D0%BD%D1%82%D1%80,_%D0%91%D0%B0%D0%BB%D1%87%D1%83%D0%B3)'

time_row = 1
prec_row = 3
temp_row = 4
press_row = 6
wind_speed_row = 7
wind_dir_row = 9
hum_row = 10


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
        dt = datetime.datetime.combine(datetime.date.today()+datetime.timedelta(days=1*days), datetime.time(h))
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


def parse_weather():
    rows = parse_page(weather_url)
    times = get_times(rows[time_row])
    prec = get_prec(rows[prec_row])
    temp = get_row_val(rows[temp_row])
    press = get_row_val(rows[press_row])
    wind_speed = get_row_val(rows[wind_speed_row])
    wind_dir = get_row_text(rows[wind_dir_row])
    hum = get_row_val(rows[hum_row])
    return{
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
