import pytest
import flask
import datetime

from src.web.client.application import app
from tests.web.data.api_test_data import sensor_data, forec_data, anomaly_data


@pytest.fixture()
def client():
    app.config['DEBUG'] = True
    client = app.test_client()
    ctx = app.app_context()
    ctx.push()

    yield client

    ctx.pop()


def test_index(client):
    resp = client.get('/')
    assert resp.status_code == 200

    resp = client.get('/index')
    assert resp.status_code == 200


def test_index_post(client):
    with client:
        resp = client.post('/index', data={'start_date': '2020-04-01', 'end_date': '2020-04-05'})
        assert resp.status_code == 200
        assert flask.session['start_date'] == datetime.datetime(2020, 4, 1).isoformat()
        assert flask.session['end_date'] == datetime.datetime(2020, 4, 5).isoformat()


def test_graph(client, requests_mock):
    requests_mock.get('http://api:8000/sensor_data', text=sensor_data)
    requests_mock.get('http://api:8000/forecast', text=forec_data)
    requests_mock.get('http://api:8000/anomaly', text=anomaly_data)
    resp = client.get('/graph')
    assert resp.status_code == 200
