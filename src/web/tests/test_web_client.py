import pytest
import flask
import datetime

from src.web.client.application import app, routes


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


def test_forecast(test_client):
    resp = test_client.get('/forecast')
    assert resp.status_code == 200


def test_history_get(test_client):
    resp = test_client.get('/history')
    assert resp.status_code == 200


def test_history_post(test_client):
    with test_client as c:
        resp = test_client.post('/history', data={'start_date': '2020-04-01', 'end_date': '2020-04-05'})
        assert resp.status_code == 200
        assert flask.session['start_date'] == datetime.datetime(2020, 4, 1).isoformat()
        assert flask.session['end_date'] == datetime.datetime(2020, 4, 5).isoformat()


def test_anomalies_get(test_client):
    resp = test_client.get('/anomalies')
    assert resp.status_code == 200


def test_anomalies_post(test_client):
    with test_client as c:
        resp = test_client.post('/anomalies', data={'start_date': '2020-04-01', 'end_date': '2020-04-05'})
        assert resp.status_code == 200
        assert flask.session['start_date'] == datetime.datetime(2020, 4, 1).isoformat()
        assert flask.session['end_date'] == datetime.datetime(2020, 4, 5).isoformat()
