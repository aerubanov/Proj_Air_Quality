import pytest
import datetime

from scripts.get_sensor_list import get_links

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
                    <a href="csv1">2019-12-02_bme280_sensor_141.csv</a>
                    </td><td align="right">2019-12-03 01:46  </td><td align="right"> 39K</td>
                    <td>&nbsp;</td></tr>
                <tr><td valign="top"><img src="/icons/text.gif" alt="[TXT]"></td><td>
                     <a href="csv2">2019-12-02_bme280_sensor_163.csv</a>
                     </td><td align="right">2019-12-03 01:46  </td><td align="right"> 41K</td>
                     <td>&nbsp;</td></tr>
                <tr><td valign="top"><img src="/icons/text.gif" alt="[TXT]"></td><td>
                <a href="csv2">2019-12-02_bme280_sensor_250.csv</a>
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


def test_get_links(mocker, requests_mock):
    date = datetime.datetime(2019, 12, 2)
    requests_mock.get('http://archive.luftdaten.info/2019-12-02/',
                      text=test_html)
    data = ''
    mock_open = mocker.mock_open(read_data=data)
    mocker.patch("builtins.open", mock_open)
    links = get_links(date.date())
    print(links)
