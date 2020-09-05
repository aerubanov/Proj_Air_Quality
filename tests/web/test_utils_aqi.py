from src.web.utils.aqi import pm25_to_aqius, aqi_level


def test_aqi_level():
    assert aqi_level(25) == 'green'
    assert aqi_level(50) == 'green'
    assert aqi_level(51) == 'gold'
    assert aqi_level(100) == 'gold'
    assert aqi_level(101) == 'orange'
    assert aqi_level(150) == 'orange'
    assert aqi_level(151) == 'red'
    assert aqi_level(200) == 'red'
    assert aqi_level(201) == 'purple'
    assert aqi_level(300) == 'purple'
    assert aqi_level(301) == 'brown'


def test_pm25_to_aqius():
    assert round(pm25_to_aqius(12)) == 50
    assert round(pm25_to_aqius(30)) == 88
    assert round(pm25_to_aqius(50)) == 136
    assert round(pm25_to_aqius(60)) == 152
    assert round(pm25_to_aqius(160)) == 210
    assert round(pm25_to_aqius(270)) == 316
