from src.web.bot.bot import get_concentration, API_HOST

sensor_data = '[{"date":"2020-04-07T12:44:06.614608","humidity":29.21038961038961,"p1":9.795701754385965,"p2":' \
          '4.26359649122807,"pressure":97008.57545454545,"temperature":14.742727272727276},' \
          '{"date":"2020-04-07T12:49:10.052534","humidity":29.264605263157897,"p1":10.31646017699115,"p2":' \
          '4.620530973451329,"pressure":96942.81236842106,"temperature":14.907368421052633},' \
          '{"date":"2020-04-07T12:54:13.287872","humidity":29.3425641025641,"p1":11.230956521739133,"p2":' \
          '5.416956521739132,"pressure":97040.5755128205,"temperature":15.036666666666665}]\n'


def test_get_concentration(requests_mock):
    requests_mock.get(API_HOST+'/sensor_data', text=sensor_data)
    anwser = get_concentration()
    assert anwser.split()[1] == '11.23'
    assert anwser.split()[3] == '5.42'
    assert anwser.split()[5] == '46.80'
    assert anwser.split()[6] == 'Good'


def test_get_forecast():
    pass
