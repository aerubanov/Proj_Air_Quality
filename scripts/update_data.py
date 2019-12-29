import datetime
import requests
import os
import csv

from scripts.config import SENSOR_ID_FILE, SERVER_URL, SENSOR_DATA_FOLDER

# This script update data for all sensors in sensor list. If data file for some sensor exist, new data will be  added
# to the file. Else, new file will be created. Default start date for checking for updates is yesterday - 30 days
# For exist file dates checked from last date with data if it later then yesterday - 30 days.


DEFAULT_DATE = datetime.date.today() - datetime.timedelta(days=30)


def check_file(fname, data_folder=SENSOR_DATA_FOLDER):
    """
    check data file
    :param fname: file name
    :param data_folder: folders with data
    :return: (True, <last timestamp value in file>) if file exist and consist data
             (False, None) otherwise
    """
    try:
        f = open(os.path.join(data_folder, fname), 'r')
        reader = csv.DictReader(f, delimiter=";")
        try:
            row = next(reversed(list(reader)))
        except StopIteration:
            return False, None
        dt = datetime.datetime.fromisoformat(row['timestamp'])
        f.close()
        return True, dt.date() + datetime.timedelta(days=1)
    except FileNotFoundError:
        return False, None


def construct_url(sensor_id, date, sensor_type):
    """generate url for download csv file with data by date"""
    url = SERVER_URL + str(date) + '/' + '_'.join([str(date), sensor_type, 'sensor', str(sensor_id)]) + '.csv'
    return url


def download_data_for_interval(start_date, end_date, filename, sensor_id, sensor_type, data_folder=SENSOR_DATA_FOLDER):
    """
    Download all data for time interval and save in one file
    :param end_date:  end point of time interval
    :param data_folder: data to store result
    :param start_date: start point of time interval
    :param filename: filename to save results
    :param sensor_id: id of sensor
    :param sensor_type: type of sensor
    :return: None
    """
    delta = end_date - start_date
    num_days = delta.days + 1
    dates = [start_date + datetime.timedelta(days=1) * i for i in range(num_days)]
    header_writen = False
    try:
        fh = open(os.path.join(data_folder, filename), "r")
        if os.stat(os.path.join(data_folder, filename)).st_size > 0:
            header_writen = True
    except FileNotFoundError:
        fh = open(os.path.join(data_folder, filename), "w")
    fh.close()
    with open(os.path.join(data_folder, filename), 'a') as f:
        for date in dates:
            url = construct_url(sensor_id, date, sensor_type)
            try:
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
            except requests.exceptions.ConnectionError as e:
                print(str(e))


def main(sensor_file):
    """ for all sensor id try update data"""
    with open(sensor_file, 'r') as sensors:
        sensor_list = sensors.read().splitlines()
        for sensor in sensor_list:
            name = sensor.split('.')[0]
            s = name.split('_')
            sensor_type = s[1]
            sensor_id = s[3]
            fname = '_'.join([sensor_id, sensor_type, 'sensor', '.csv'])
            file_exist, date = check_file(fname)
            if date is None:
                date = DEFAULT_DATE
            yesterday = datetime.date.today() - datetime.timedelta(days=1)
            date = max(DEFAULT_DATE, date)
            download_data_for_interval(date, yesterday, fname, sensor_id, sensor_type)
            print(sensor)


if __name__ == '__main__':
    main(SENSOR_ID_FILE)
