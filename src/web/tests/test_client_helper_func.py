from src.web.client.application.helper_functions import aqi_level, pm25_to_aqius


def test_aqi_level():
    assert aqi_level(25) == 'good'
    assert aqi_level(50) == 'good'
    assert aqi_level(51) == 'moderate'
    assert aqi_level(100) == 'moderate'
    assert aqi_level(101) == 'Unhealthy for sens. groups'
    assert aqi_level(150) == 'Unhealthy for sens. groups'
    assert aqi_level(151) == "Unhealthy"
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
