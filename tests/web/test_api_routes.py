import pytest
import datetime
import json

from src.web.api.application import app
from src.web.models.model import Sensors, Forecast, Anomaly


@pytest.fixture()
def api_test_client():
    app.config['DATABASE'] = app.config['TEST_DATABASE']
    app.config['DEBUG'] = True
    testing_client = app.test_client()
    ctx = app.app_context()
    ctx.push()

    yield testing_client

    ctx.pop()


def test_get_sensor_data_correct_request(database_session, api_test_client):
    s1 = Sensors(date=datetime.datetime(2020, 2, 12, 15, 30, 4), p1=6.7, p2=4.7)
    s2 = Sensors(date=datetime.datetime(2020, 2, 15, 11, 44, 6), p1=6.7, p2=4.7)
    database_session.add(s1)
    database_session.add(s2)
    database_session.commit()

    resp = api_test_client.get('/sensor_data', json={"start_time": "2020-02-10T00:00:00",
                                                     "end_time": "2020-02-16T00:00:00"},
                               content_type='application/json')

    assert resp.status_code == 200
    resp_data = json.loads(resp.data)
    assert len(resp_data) == 2
    assert resp_data[0]['date'] == "2020-02-12T15:30:04"
    assert resp_data[1]['date'] == "2020-02-15T11:44:06"

    resp = api_test_client.get('/sensor_data', json={"start_time": "2020-02-13T00:00:00",
                                                     "end_time": "2020-02-16T00:00:00"},
                               content_type='application/json')

    assert resp.status_code == 200
    resp_data = json.loads(resp.data)
    assert len(resp_data) == 1
    assert resp_data[0]['date'] == "2020-02-15T11:44:06"


def test_get_sensor_data_incorrect_request(database_session, api_test_client):
    s1 = Sensors(date=datetime.datetime(2020, 2, 12, 15, 30, 4), p1=6.7, p2=4.7)
    s2 = Sensors(date=datetime.datetime(2020, 2, 15, 11, 44, 6), p1=6.7, p2=4.7)
    database_session.add(s1)
    database_session.add(s2)
    database_session.commit()

    resp = api_test_client.get('/sensor_data', json={"start_time": "2020-02-20T00:00:00",
                                                     "end_time": "2020-02-16T00:00:00"},
                               content_type='application/json')

    assert resp.status_code == 400


def test_get_sensor_data_with_columns(database_session, api_test_client):
    s1 = Sensors(date=datetime.datetime(2020, 2, 12, 15, 30, 4), p1=6.7, p2=4.7,
                 temperature=22, humidity=65, pressure=99679)
    s2 = Sensors(date=datetime.datetime(2020, 2, 15, 11, 44, 6), p1=7.7, p2=5.7,
                 temperature=22, humidity=65, pressure=99679)
    database_session.add(s1)
    database_session.commit()
    database_session.add(s2)
    database_session.commit()

    columns = ['date', 'p1', 'p2']
    resp = api_test_client.get('/sensor_data', json={"start_time": "2020-02-12T00:00:00",
                                                     "end_time": "2020-02-16T00:00:00",
                                                     "columns": columns},
                               content_type='application/json')
    assert resp.status_code == 200
    resp_data = json.loads(resp.data)
    assert len(resp_data) == 2
    for item in resp_data:
        for column in columns:
            assert column in item


def test_get_forecast_without_date(database_session, api_test_client):
    f1 = Forecast(date=datetime.datetime(2020, 3, 1, 9, 0, 0), forward_time=0)
    f2 = Forecast(date=datetime.datetime(2020, 3, 1, 10, 0, 0), forward_time=0)
    f3 = Forecast(date=datetime.datetime(2020, 3, 1, 10, 0, 0), forward_time=1)
    database_session.add(f1)
    database_session.add(f2)
    database_session.add(f3)
    database_session.commit()

    resp = api_test_client.get('/forecast', json={},
                               content_type='application/json')

    assert resp.status_code == 200
    resp_data = json.loads(resp.data)
    assert len(resp_data) == 2
    assert resp_data[0]['date'] == "2020-03-01T10:00:00"
    assert resp_data[1]['date'] == "2020-03-01T10:00:00"


def test_get_forecast_with_start_date(database_session, api_test_client):
    f1 = Forecast(date=datetime.datetime(2020, 3, 1, 9, 0, 0), forward_time=0)
    f2 = Forecast(date=datetime.datetime(2020, 3, 1, 10, 0, 0), forward_time=0)
    f3 = Forecast(date=datetime.datetime(2020, 3, 2, 10, 0, 0), forward_time=0)
    database_session.add(f1)
    database_session.add(f2)
    database_session.add(f3)
    database_session.commit()

    resp = api_test_client.get('/forecast', json={'start_time': "2020-03-01T09:03:00"},
                               content_type='application/json')

    assert resp.status_code == 200
    resp_data = json.loads(resp.data)
    assert len(resp_data) == 2
    assert resp_data[1]['date'] == "2020-03-01T10:00:00"
    assert resp_data[0]['date'] == "2020-03-02T10:00:00"


def test_get_forecast_with_end_date(database_session, api_test_client):
    f1 = Forecast(date=datetime.datetime(2020, 3, 1, 9, 0, 0), forward_time=0)
    f2 = Forecast(date=datetime.datetime(2020, 3, 1, 10, 0, 0), forward_time=0)
    f3 = Forecast(date=datetime.datetime(2020, 3, 2, 10, 0, 0), forward_time=0)
    database_session.add(f1)
    database_session.add(f2)
    database_session.add(f3)
    database_session.commit()

    resp = api_test_client.get('/forecast', json={'end_time': "2020-03-01T11:00:00"},
                               content_type='application/json')

    assert resp.status_code == 200
    resp_data = json.loads(resp.data)
    assert len(resp_data) == 2
    assert resp_data[1]['date'] == "2020-03-01T09:00:00"
    assert resp_data[0]['date'] == "2020-03-01T10:00:00"


def test_get_forecast_start_and_end_date(database_session, api_test_client):
    f1 = Forecast(date=datetime.datetime(2020, 3, 1, 9, 0, 0), forward_time=0)
    f2 = Forecast(date=datetime.datetime(2020, 3, 1, 10, 0, 0), forward_time=0)
    f3 = Forecast(date=datetime.datetime(2020, 3, 2, 10, 0, 0), forward_time=0)
    database_session.add(f1)
    database_session.add(f2)
    database_session.add(f3)
    database_session.commit()

    resp = api_test_client.get('/forecast', json={'start_time': '2020-03-01T09:30:00',
                                                  'end_time': "2020-03-01T11:00:00"},
                               content_type='application/json')

    assert resp.status_code == 200
    resp_data = json.loads(resp.data)
    assert len(resp_data) == 1
    assert resp_data[0]['date'] == "2020-03-01T10:00:00"


def test_get_forecast_incorrect_request(database_session, api_test_client):
    f1 = Forecast(date=datetime.datetime(2020, 3, 1, 9, 0, 0), forward_time=0)
    f2 = Forecast(date=datetime.datetime(2020, 3, 1, 10, 0, 0), forward_time=0)
    f3 = Forecast(date=datetime.datetime(2020, 3, 2, 10, 0, 0), forward_time=0)
    database_session.add(f1)
    database_session.add(f2)
    database_session.add(f3)
    database_session.commit()

    resp = api_test_client.get('/forecast', json={'end_time': '2020-03-01T09:30:00',
                                                  'start_time': "2020-03-01T11:00:00"},
                               content_type='application/json')

    assert resp.status_code == 400


def test_get_anomaly_correct(database_session, api_test_client):
    a1 = Anomaly(start_date=datetime.datetime(2020, 3, 18, 9, 0, 0),
                 end_date=datetime.datetime(2020, 3, 18, 9, 20, 0))
    a2 = Anomaly(start_date=datetime.datetime(2020, 3, 18, 9, 20, 0),
                 end_date=datetime.datetime(2020, 3, 18, 9, 40, 0))
    a3 = Anomaly(start_date=datetime.datetime(2020, 3, 18, 10, 0, 0),
                 end_date=datetime.datetime(2020, 3, 18, 10, 10, 0))
    a4 = Anomaly(start_date=datetime.datetime(2020, 3, 18, 10, 30, 0),
                 end_date=datetime.datetime(2020, 3, 18, 10, 40, 0))
    a5 = Anomaly(start_date=datetime.datetime(2020, 3, 18, 11, 0, 0),
                 end_date=datetime.datetime(2020, 3, 18, 12, 0, 0))
    database_session.add(a1)
    database_session.add(a2)
    database_session.add(a3)
    database_session.add(a4)
    database_session.add(a5)
    database_session.commit()
    resp = api_test_client.get('/anomaly', json={'start_time': '2020-03-18T09:30:00',
                                                 'end_time': "2020-03-18T10:35:00"},
                               content_type='application/json')
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert len(data) == 3
    assert data[0]['start_date'] == datetime.datetime(2020, 3, 18, 9, 20, 0).isoformat('T')
    assert data[1]['start_date'] == datetime.datetime(2020, 3, 18, 10, 00, 0).isoformat('T')
    assert data[2]['start_date'] == datetime.datetime(2020, 3, 18, 10, 30, 0).isoformat('T')


def test_get_anomaly_incorrect_request(database_session, api_test_client):
    a1 = Anomaly(start_date=datetime.datetime(2020, 3, 18, 9, 0, 0),
                 end_date=datetime.datetime(2020, 3, 18, 9, 20, 0))
    a2 = Anomaly(start_date=datetime.datetime(2020, 3, 18, 9, 20, 0),
                 end_date=datetime.datetime(2020, 3, 18, 9, 40, 0))
    a3 = Anomaly(start_date=datetime.datetime(2020, 3, 18, 10, 0, 0),
                 end_date=datetime.datetime(2020, 3, 18, 10, 10, 0))
    a4 = Anomaly(start_date=datetime.datetime(2020, 3, 18, 10, 30, 0),
                 end_date=datetime.datetime(2020, 3, 18, 10, 40, 0))
    a5 = Anomaly(start_date=datetime.datetime(2020, 3, 18, 11, 0, 0),
                 end_date=datetime.datetime(2020, 3, 18, 12, 0, 0))
    database_session.add(a1)
    database_session.add(a2)
    database_session.add(a3)
    database_session.add(a4)
    database_session.add(a5)
    database_session.commit()
    resp = api_test_client.get('/anomaly', json={'end_time': '2020-03-18T09:30:00'},
                               content_type='application/json')
    assert resp.status_code == 400
    resp = api_test_client.get('/anomaly', json={'start_time': "2020-03-18T10:35:00"},
                               content_type='application/json')
    assert resp.status_code == 400
    resp = api_test_client.get('/anomaly', json={'end_time': '2020-03-18T09:30:00',
                                                 'start_time': "2020-03-18T10:35:00"},
                               content_type='application/json')
    assert resp.status_code == 400
