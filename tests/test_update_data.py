import datetime

from src.data.config import SERVER_URL
from src.data.update_data import construct_url, check_file, download_data_for_interval


def test_construct_url():
    sensor_id = 111
    sensor_type = 'type'
    date = datetime.datetime(2019, 12, 5).date()
    result = construct_url(sensor_id, date, sensor_type)
    assert result == SERVER_URL + '2019-12-05/2019-12-05_type_sensor_111.csv'


def test_check_file(tmpdir):
    dir_name = 'test_data'
    d = tmpdir.mkdir(dir_name)

    res = check_file('some_file.csv', data_folder=dir_name)
    assert res == (False, None)

    f1 = d.join("empty.csv")
    f1.write('')
    res = check_file(f1, data_folder=dir_name)
    assert res == (False, None)

    f2 = d.join("data.csv")
    f2.write("sensor_id;sensor_type;location;lat;lon;timestamp;P1;durP1;ratioP1;P2;durP2;ratioP2\n"
             "19649;SDS011;9973;55.686;37.589;2019-01-10T19:05:56;15.77;;;7.95;;\n"
             "19649;SDS011;12232;55.728;37.476;2019-11-03T23:58:34;5.63;;;4.70;;\n")
    res = check_file(f2, data_folder=dir_name)
    assert res == (True, datetime.datetime(2019, 11, 4).date())


def test_download_data_for_interval(tmpdir, requests_mock):
    dir_name = 'test_data'
    d = tmpdir.mkdir(dir_name)
    date1 = datetime.datetime(2019, 12, 4).date()
    date2 = datetime.datetime(2019, 12, 5).date()
    sensor_id = '111'
    sensor_type = 'type'
    fname = '_'.join([sensor_id, sensor_type, 'sensor', '.csv'])
    data_04 = "sensor_id;sensor_type;location;lat;lon;timestamp;P1;durP1;ratioP1;P2;durP2;ratioP2\n" \
              "19649;SDS011;9973;55.686;37.589;2019-12-04T19:05:56;15.77;;;7.95;;\n"
    data_05 = "sensor_id;sensor_type;location;lat;lon;timestamp;P1;durP1;ratioP1;P2;durP2;ratioP2\n" \
              "19649;SDS011;12232;55.728;37.476;2019-11-03T23:58:34;5.63;;;4.70;;\n"
    requests_mock.get(SERVER_URL + '2019-12-05/2019-12-05_type_sensor_111.csv',
                      content=bytes(data_05, 'utf-8'))
    requests_mock.get(SERVER_URL + '2019-12-04/2019-12-04_type_sensor_111.csv',
                      content=bytes(data_04, 'utf-8'))
    f1 = d.join(fname)
    f1.write('')
    download_data_for_interval(date1, date2, f1, sensor_id, sensor_type)
    assert f1.read().splitlines() == [
        'sensor_id;sensor_type;location;lat;lon;timestamp;P1;durP1;ratioP1;P2;durP2;ratioP2',
        '19649;SDS011;9973;55.686;37.589;2019-12-04T19:05:56;15.77;;;7.95;;',
        '19649;SDS011;12232;55.728;37.476;2019-11-03T23:58:34;5.63;;;4.70;;']
    download_data_for_interval(date1, date2, f1, sensor_id, sensor_type)
    assert f1.read().splitlines() == [
        'sensor_id;sensor_type;location;lat;lon;timestamp;P1;durP1;ratioP1;P2;durP2;ratioP2',
        '19649;SDS011;9973;55.686;37.589;2019-12-04T19:05:56;15.77;;;7.95;;',
        '19649;SDS011;12232;55.728;37.476;2019-11-03T23:58:34;5.63;;;4.70;;',
        '19649;SDS011;9973;55.686;37.589;2019-12-04T19:05:56;15.77;;;7.95;;',
        '19649;SDS011;12232;55.728;37.476;2019-11-03T23:58:34;5.63;;;4.70;;']
