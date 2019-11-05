import datetime
import requests
import os
import time

# filename patterns for specifying sensors types
DATA_FOLDER = '../DATA/'
SERVER_URL = 'http://archive.luftdaten.info/'
BME280 = '_bme280_sensor_'
BMP180 = '_bmp180_sensor_'
BMP280 = '_bmp280_sensor_'
DHT22 = '_dht22_sensor_'
DS18B20 = '_ds18b20_sensor_'
HPM = '_hpm_sensor_'
HTU21D = '_htu21d_sensor_'
LAERM = '_laerm_sensor_'
PMS1003 = '_pms1003_sensor_'
PMS3003 = '_pms3003_sensor_'
PMS5003 = '_pms5003_sensor_'
PMS7003 = '_pms7003_sensor_'
PPD42NS = '_ppd42ns_sensor_'
SDS011 = '_sds011_sensor_'

# list of SDS011 particle concentration sensors in Moscow on 18.10.2019
pm_sensor_id_list = [26014, 26251, 24797, 26219, 31766, 28509, 26191, 32709, 20219, 30289, 20225, 22314, 24028,
                     24088, 25083, 23200, 23294, 28802, 25021, 28401, 19836, 32465, 19649, 24026, 25561, 27418,
                     31668, 32487, 32226, 32403, 23150, 24309, 32756, 32802, 19838, 20229, 23512, 22044, 32439,
                     32772, 32866, 22632, 24052, 26058, 27213, 23317, 24687, 28286, 30669, 31087, 31862, 30810,
                     30920, 31174, 31650, 32074, 24997, 30529, 30731, 30862, 32337, 32407]
# list of BME280 temperature and humidity sensor in Moscow on 18.10.2019
bme_temp_sensor_id_list = [31767, 26220, 32791, 28510, 26192, 24029, 25084, 23201, 23295, 31669, 32227, 32488,
                           24027, 32466, 32404, 32867, 32440, 20228, 23516, 22045, 26059, 27214, 24688, 31175,
                           23318, 31088, 24578, 30530, 30732, 30905, 30921, 32075, 32338, 24998]
# list of DHT22 temperature and humidity sensor in Moscow on 18.10.2019
dht_temp_sensor_id_list = [30351, 28905, 22633]


def construct_url(sensor_id, date, sensor_type):
    """generate url for download csv file with data by date"""
    url = SERVER_URL + str(date) + '/' + str(date) + sensor_type + str(sensor_id) + '.csv'
    return url


def download_data_for_interval(start_date, num_days, filename, sensor_id, sensor_type):
    """
    Download all data for time interval and save in one file
    :param start_date: start point of time interval
    :param num_days: number of days from start_date to download data
    :param filename: filename to save results
    :param sensor_id: id of sensor
    :param sensor_type: type of sensor
    :return: None
    """
    dates = [start_date + datetime.timedelta(days=1) * i for i in range(num_days)]
    header_writen = False
    with open(os.path.join(DATA_FOLDER, filename), 'w') as f:
        for date in dates:
            url = construct_url(sensor_id, date, sensor_type)
            resp = requests.get(url)
            if resp.status_code == 200:
                if header_writen:
                    data = resp.content.decode().splitlines()[1:]
                    f.write('\n'.join(data))
                    f.write('\n')
                else:
                    data = resp.content.decode()
                    f.write(data)
                    header_writen = True


def download_pm(start_date, num_days):
    try:
        fh = open('downloaded_list.txt', "r")
    except FileNotFoundError:
        fh = open('downloaded_list.txt', "w")
    fh.close()
    with open('downloaded_list.txt', 'r+') as proc_file:
        downloaded_files = proc_file.read().splitlines()
        id_list = pm_sensor_id_list
        for s_id in id_list:
            f_name = str(s_id) + SDS011 + '.csv'
            if f_name not in downloaded_files:
                download_data_for_interval(start_date, num_days, f_name, s_id, SDS011)
                print(f_name)
                downloaded_files.append(f_name)
                proc_file.write(f_name+'\n')


def download_temp_bme(start_date, num_days):
    try:
        fh = open('downloaded_list.txt', "r")
    except FileNotFoundError:
        fh = open('downloaded_list.txt', "w")
    fh.close()
    with open('downloaded_list.txt', 'r+') as proc_file:
        downloaded_files = proc_file.read().splitlines()
        id_list = bme_temp_sensor_id_list
        for s_id in id_list:
            f_name = str(s_id) + BME280 + '.csv'
            if f_name not in downloaded_files:
                download_data_for_interval(start_date, num_days, f_name, s_id, BME280)
                print(f_name)
                downloaded_files.append(f_name)
                proc_file.write(f_name+'\n')


def download_temp_dht(start_date, num_days):
    try:
        fh = open('downloaded_list.txt', "r")
    except FileNotFoundError:
        fh = open('downloaded_list.txt', "w")
    fh.close()
    with open('downloaded_list.txt', 'r+') as proc_file:
        downloaded_files = proc_file.read().splitlines()
        id_list = dht_temp_sensor_id_list
        for s_id in id_list:
            f_name = str(s_id) + DHT22 + '.csv'
            if f_name not in downloaded_files:
                download_data_for_interval(start_date, num_days, f_name, s_id, DHT22)
                print(f_name)
                downloaded_files.append(f_name)
                proc_file.write(f_name+'\n')


if __name__ == '__main__':
    d = datetime.date(2018, 11, 4)
    n_days = 365
    while True:
        try:
            download_pm(d, n_days)
            download_temp_bme(d, n_days)
            download_temp_dht(d, n_days)
            break
        except requests.exceptions.ConnectionError:
            print("Connection error")
            time.sleep(10)
