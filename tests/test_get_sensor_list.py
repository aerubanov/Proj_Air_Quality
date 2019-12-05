import datetime

from scripts.get_sensor_list import get_links, check_sensor_pos, check_coordinate
from scripts.config import MIN_LON, MAX_LON, MIN_LAT, MAX_LAT

test_html = '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
                <html>
                 <head>
                  <title>Index of /2019-12-02</title>
                 </head>
                 <body>
                <h1>Index of /2019-12-02</h1>
                  <table>
                   <tr><th valign="top"><img src="/icons/blank.gif" alt="[ICO]">
                   </th><th><a href="?C=N;O=D">Name</a></th><th><a href="?C=M;O=A">Last modified</a>
                   </th><th><a href="?C=S;O=A">Size</a></th><th><a href="?C=D;O=A">Description</a>
                   </th></tr>
                   <tr><th colspan="5"><hr></th></tr>
                <tr><td valign="top"><img src="/icons/back.gif" alt="[PARENTDIR]"></td><td>
                    <a href="/">Parent Directory</a></td><td>&nbsp;</td>
                    <td align="right">  - </td><td>&nbsp;</td></tr>
                <tr><td valign="top"><img src="/icons/text.gif" alt="[TXT]"></td><td>
                    <a href="2019-12-02_csv1">2019-12-02_bme280_sensor_141.csv</a>
                    </td><td align="right">2019-12-03 01:46  </td><td align="right"> 39K</td>
                    <td>&nbsp;</td></tr>
                <tr><td valign="top"><img src="/icons/text.gif" alt="[TXT]"></td><td>
                     <a href="2019-12-02_csv2">2019-12-02_bme280_sensor_163.csv</a>
                     </td><td align="right">2019-12-03 01:46  </td><td align="right"> 41K</td>
                     <td>&nbsp;</td></tr>
                <tr><td valign="top"><img src="/icons/text.gif" alt="[TXT]"></td><td>
                     <a href="2019-12-02_csv3">2019-12-02_bme280_sensor_250.csv</a>
                    </td><td align="right">2019-12-03 01:46  </td><td align="right"> 41K</td>
                    <td>&nbsp;</td></tr>
                <tr><td valign="top"><img src="/icons/text.gif" alt="[TXT]"></td><td>
                    <a href="measurements.txt">measurements.txt</a>
                    </td><td align="right">2019-12-03 01:47  </td>
                    <td align="right">  8 </td><td>&nbsp;</td></tr>
                <tr><td valign="top"><img src="/icons/text.gif" alt="[TXT]"></td><td>
                    <a href="sensor_count.txt">sensor_count.txt</a>
                    </td><td align="right">2019-12-03 01:47  </td>
                    <td align="right">243 </td><td>&nbsp;</td></tr>
                    <tr><th colspan="5"><hr></th></tr>
                </table>
                <address>Apache/2.4.39 (Ubuntu) Server at archive.luftdaten.info Port 80</address>
                </body></html>
                '''


def test_get_links(tmpdir, requests_mock):
    date = datetime.datetime(2019, 12, 2)
    requests_mock.get('http://archive.luftdaten.info/2019-12-02/',
                      text=test_html)
    p = tmpdir.mkdir("data").join("test_links.txt")
    data = ''  # no already seen files
    p.write(data)
    print(p)
    links = get_links(date.date(), p)
    assert links == [
        'http://archive.luftdaten.info/2019-12-02/2019-12-02_csv1',
        'http://archive.luftdaten.info/2019-12-02/2019-12-02_csv2',
        'http://archive.luftdaten.info/2019-12-02/2019-12-02_csv3',
    ]
    data = "2019-12-02_csv1"  # already seen first file
    p.write(data)
    links = get_links(date.date(), p)
    assert links == ['http://archive.luftdaten.info/2019-12-02/2019-12-02_csv2',
                     'http://archive.luftdaten.info/2019-12-02/2019-12-02_csv3']
    assert p.read() == data


def test_check_sensor_pos(tmpdir, requests_mock):
    links = ['http://archive.luftdaten.info/2019-12-02/2019-12-02_csv1',
             'http://archive.luftdaten.info/2019-12-02/2019-12-02_csv2']

    appropriate_sensor = "sensor_id;sensor_type;location;lat;lon;timestamp;P1;durP1;ratioP1;P2;durP2;ratioP2 \n " \
                         "19649;SDS011;9973;55.686;37.589;2019-01-10T19:05:56;15.77;;;7.95;;"
    inappropriate_sensor = "sensor_id;sensor_type;location;lat;lon;timestamp;P1;durP1;ratioP1;P2;durP2;ratioP2 \n " \
                           "19649;SDS011;9973;10.686;22.589;2019-01-10T19:05:56;15.77;;;7.95;;"

    requests_mock.get('http://archive.luftdaten.info/2019-12-02/2019-12-02_csv1',
                      content=bytes(appropriate_sensor, 'utf-8'))
    requests_mock.get('http://archive.luftdaten.info/2019-12-02/2019-12-02_csv2',
                      content=bytes(inappropriate_sensor, 'utf-8'))

    d = tmpdir.mkdir("data")
    link_file = d.join("test_links.txt")
    id_file = d.join("sensor_id.txt")
    link_file.write('some_link'+'\n')
    id_file.write('some_id'+'\n')

    check_sensor_pos(links, link_file, id_file)

    assert 'some_link' in link_file.read().splitlines()
    assert '2019-12-02_csv1' in link_file.read().splitlines()
    assert '2019-12-02_csv2' in link_file.read().splitlines()

    assert 'some_id' in id_file.read().splitlines()
    assert '_csv1' in id_file.read().splitlines()
    assert '_csv2' not in id_file.read().splitlines()


def test_check_coordinate():
    assert check_coordinate(MIN_LAT + (MAX_LAT - MIN_LAT)/2, MIN_LON + (MAX_LON - MIN_LON)/2)
    assert not check_coordinate(MIN_LAT-1, MIN_LON + (MAX_LON - MIN_LON)/2)
    assert not check_coordinate(MAX_LAT+1, MIN_LON + (MAX_LON - MIN_LON)/2)
    assert not check_coordinate(MIN_LAT + (MAX_LAT - MIN_LAT) / 2, MIN_LON-1)
    assert not check_coordinate(MIN_LAT + (MAX_LAT - MIN_LAT) / 2, MAX_LON+1)
