import pytest
import flask
import datetime

from src.web.client.application import app, routes
from tests.web.data.api_test_data import sensor_data, forec_data, anomaly_data


@pytest.fixture()
def test_client():
    app.config['DEBUG'] = True
    testing_client = app.test_client()
    ctx = app.app_context()
    ctx.push()

    yield testing_client

    ctx.pop()


def test_index(test_client):
    resp = test_client.get('/')
    assert resp.status_code == 200
    resp = test_client.get('/index')
    assert resp.status_code == 200


def test_index_post(test_client):
    with test_client:
        resp = test_client.post('/index', data={'start_date': '2020-04-01', 'end_date': '2020-04-05'})
        assert resp.status_code == 200
        assert flask.session['start_date'] == datetime.datetime(2020, 4, 1).isoformat()
        assert flask.session['end_date'] == datetime.datetime(2020, 4, 5).isoformat()


def test_graph(test_client, requests_mock):
    requests_mock.get('http://api:8000/sensor_data', text=sensor_data)
    requests_mock.get('http://api:8000/forecast', text=forec_data)
    requests_mock.get('http://api:8000/anomaly', text=anomaly_data)
    resp = test_client.get('/graph')
    assert resp.status_code == 200
