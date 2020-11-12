import numpy as np

from src.web.server.loader.sensor_loading import read_sensor_id, average_data, load_data, api_url, filter_average


def test_read_sensor_id(tmpdir):
    p = tmpdir.mkdir("data").join("test_links.txt")
    data = """,sensor_id,sensor_type,lat,lon\n
            0,26717,BME280,55.684,37.584\n
            1,32440,BME280,55.81110008,37.72890151\n
            2,35435,BME280,55.782,37.528\n
            3,36948,BME280,55.69,37.574\n"""
    p.write(data)
    s_id = read_sensor_id(p)
    assert s_id == {26717, 32440, 35435, 36948}


def test_filter_average():
    data = np.array([0, 4, 5, 6, 10])
    assert np.isclose(5, filter_average(data))


def test_average_data(monkeypatch):
    test_data = [
        {'id': 31767, 'humidity': '85.74', 'pressure': '97354.17', 'temperature':
            '0.06', 'pressure_at_sealevel': 99482.08},
        {'id': 31862, 'P1': '15', 'P2': '1.75'},
        {'id': 32074, 'P1': '5.28', 'P2': '35.5'},
        {'id': 32075, 'humidity': '75.34', 'pressure': '96792.30', 'temperature': '-0.22',
         'pressure_at_sealevel': 98897.79},
        {'id': 32226, 'P1': '5.62', 'P2': '9.98'},
        {'id': 32337, 'P1': '1', 'P2': '7.64'},
    ]

    def mockreturn(d):
        assert isinstance(d, np.ndarray)
        return 1

    monkeypatch.setattr('src.web.server.loader.sensor_loading.filter_average', mockreturn)

    data = average_data(test_data)
    assert 'p1' in data
    assert 'p2' in data
    assert 'hum' in data
    assert 'press' in data
    assert 'temp' in data
    assert data['p1'] == 1
    assert data['p2'] == 1
    assert data['hum'] == 1
    assert data['press'] == 1
    assert data['temp'] == 1


def test_load_data(requests_mock):
    test_data = """[{"id":6169764730,"sampling_rate":null,"timestamp":"2020-01-22 14:33:47",
    "location":{"id":13208,"latitude":"51.044","longitude":"13.746","altitude":"115.3","country":"DE",
    "exact_location":0,"indoor":1},"sensor":{"id":36,"pin":"1","sensor_type":{"id":14,"name":"SDS011",
    "manufacturer":"Nova Fitness"}},"sensordatavalues":[{"id":13109424441,"value":"39.50","value_type":"humidity"}]},
    {"id":6169764636,"sampling_rate":null,"timestamp":"2020-01-22 14:33:46","location":{"id":13208,"latitude":"51.044",
    "longitude":"13.746","altitude":"115.3","country":"DE","exact_location":0,"indoor":0},"sensor":{"id":1356,"pin":"1",
    "sensor_type":{"id":14,"name":"SDS011","manufacturer":"Nova Fitness"}},"sensordatavalues":[{"id":13109424235,
    "value":"0.20","value_type":"P1"},{"id":13109424236,"value":"0.20","value_type":"P2"}]},{"id":6169764730,
    "sampling_rate":null,"timestamp":"2020-01-22 14:33:47","location":{"id":13208,"latitude":"51.044",
    "longitude":"13.746","altitude":"115.3","country":"DE","exact_location":0,"indoor":0},"sensor":
    {"id":2363,"pin":"1","sensor_type":{"id":14,"name":"SDS011","manufacturer":"Nova Fitness"}},
    "sensordatavalues":[{"id":13109424440,"value":"24.30","value_type":"temperature"}]},
    {"id":6169768104,"sampling_rate":null,"timestamp":"2020-01-22 14:34:06",
    "location":{"id":7517,"latitude":"48.4","longitude":"11.77","altitude":"442.2","country":"DE","exact_location":0,
    "indoor":0},"sensor":{"id":14850,"pin":"7","sensor_type":{"id":9,"name":"DHT22","manufacturer":"various"}},
    "sensordatavalues":[{"id":13109431620,"value":"66.45","value_type":"humidity"},
    {"id":13109431619,"value":"5.50","value_type":"temperature"},
    {"id":13109434257,"value":"102927.78","value_type":"pressure"}]}]"""
    s_id = {36, 1356, 14850}
    requests_mock.get(api_url,
                      text=test_data)
    data = load_data(s_id)
    assert set([i['id'] for i in data]) == {1356, 14850}  # id 36 is indoor!
    assert 'P1' in data[0] and 'P2' in data[0]
    assert "humidity" in data[1]
    assert "pressure" in data[1]
    assert "temperature" in data[1]
