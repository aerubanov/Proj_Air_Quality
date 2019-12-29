import datetime
import requests
import os
import csv

from scripts.config import WATHER_DATA_FOLDER

DEFAULT_DATE = datetime.date.today() - datetime.timedelta(days=30)


def check_file(fname, data_folder=WATHER_DATA_FOLDER):
    """
    checking existing wather data
    :param fname: file name for checking
    :param data_folder: path to folder
    :return: (True, last_date) if file with data exist, (False, None) otherwise
    """
    try:
        f = open(os.path.join(data_folder, fname), 'r')
        for i in range(6):
            f.readline()
        reader = csv.DictReader(f, delimiter=";")
        try:
            row = next(reader)
        except StopIteration:
            return False, None
        t = row['Местное время в Москве (центр, Балчуг)']
        t = t.split()[0].split('.')
        day = int(t[0])
        month = int(t[1])
        year = int(t[2])
        dt = datetime.datetime(year, month, day)
        print(t)
        f.close()
        return True, dt.date() + datetime.timedelta(days=1)
    except FileNotFoundError:
        return False, None