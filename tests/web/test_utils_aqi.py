from src.web.utils.aqi import pm25_to_aqius, aqi_level


def test_aqi_level():
    assert aqi_level(25) == 'Good'
    assert aqi_level(50) == 'Good'
    assert aqi_level(51) == 'Moderate'
    assert aqi_level(100) == 'Moderate'
    assert aqi_level(101) == 'Unhealthy for Sensitive Groups'
    assert aqi_level(150) == 'Unhealthy for Sensitive Groups'
    assert aqi_level(151) == 'Unhealthy'
    assert aqi_level(200) == 'Unhealthy'
    assert aqi_level(201) == 'Very Unhealthy'
    assert aqi_level(300) == 'Very Unhealthy'
    assert aqi_level(301) == 'Hazardous'


def test_pm25_to_aqius():
    assert round(pm25_to_aqius(12)) == 50
    assert round(pm25_to_aqius(30)) == 88
    assert round(pm25_to_aqius(50)) == 136
    assert round(pm25_to_aqius(60)) == 152
    assert round(pm25_to_aqius(160)) == 210
    assert round(pm25_to_aqius(270)) == 316
