import pytest
import flask
import datetime

from src.web.client.application import app, routes

sensor_data = '[{"date":"2020-04-07T12:44:06.614608","humidity":29.21038961038961,"p1":9.795701754385965,"p2":' \
          '4.26359649122807,"pressure":97008.57545454545,"temperature":14.742727272727276},' \
          '{"date":"2020-04-07T12:49:10.052534","humidity":29.264605263157897,"p1":10.31646017699115,"p2":' \
          '4.620530973451329,"pressure":96942.81236842106,"temperature":14.907368421052633},' \
          '{"date":"2020-04-07T12:54:13.287872","humidity":29.3425641025641,"p1":11.230956521739133,"p2":' \
          '5.416956521739132,"pressure":97040.5755128205,"temperature":15.036666666666665}]\n'

forec_data = '[{"date":"2020-04-07T13:01:00.715570","forward_time":1,"p1":9.903963289614435,"p2":4.538788272920509},' \
            '{"date":"2020-04-07T13:01:00.715570","forward_time":2,"p1":9.99440164525862,"p2":4.813549213711938},' \
            '{"date":"2020-04-07T13:01:00.715570","forward_time":3,"p1":10.114635098325737,"p2":5.022647729478597},' \
            '{"date":"2020-04-07T13:01:00.715570","forward_time":4,"p1":10.166772386513276,"p2":5.279910683334124},' \
            '{"date":"2020-04-07T13:01:00.715570","forward_time":5,"p1":10.54555315288079,"p2":5.484178099480452},' \
            '{"date":"2020-04-07T13:01:00.715570","forward_time":6,"p1":11.13673546333013,"p2":5.7430700124145115},' \
            '{"date":"2020-04-07T13:01:00.715570","forward_time":7,"p1":11.625170842700726,"p2":5.760572092491813},' \
            '{"date":"2020-04-07T13:01:00.715570","forward_time":8,"p1":12.294349456161914,"p2":5.920252902585343},' \
             '{"date":"2020-04-07T13:01:00.715570","forward_time":9,"p1":12.751372291011094,"p2":6.105632773307496},' \
             '{"date":"2020-04-07T13:01:00.715570","forward_time":10,"p1":13.212773170464814,"p2":6.322940353359478},' \
             '{"date":"2020-04-07T13:01:00.715570","forward_time":11,"p1":14.00267367565171,"p2":6.483225001772104},' \
             '{"date":"2020-04-07T13:01:00.715570","forward_time":12,"p1":14.136950740439588,"p2":6.551975303199027},' \
             '{"date":"2020-04-07T13:01:00.715570","forward_time":13,"p1":14.484600395733235,"p2":6.53612438144909},' \
             '{"date":"2020-04-07T13:01:00.715570","forward_time":14,"p1":14.20749741374226,"p2":6.474517430819663},' \
             '{"date":"2020-04-07T13:01:00.715570","forward_time":15,"p1":13.780582694630006,"p2":6.409140847568311},' \
             '{"date":"2020-04-07T13:01:00.715570","forward_time":16,"p1":13.520960771341691,"p2":6.36028858244422},' \
             '{"date":"2020-04-07T13:01:00.715570","forward_time":17,"p1":13.380508465219034,"p2":6.246610951247378},' \
             '{"date":"2020-04-07T13:01:00.715570","forward_time":18,"p1":13.124528704734905,"p2":6.13341727335296},' \
             '{"date":"2020-04-07T13:01:00.715570","forward_time":19,"p1":13.042411134670974,"p2":6.103850570216498},' \
             '{"date":"2020-04-07T13:01:00.715570","forward_time":20,"p1":13.299037381600328,"p2":5.957039210777239},' \
             '{"date":"2020-04-07T13:01:00.715570","forward_time":21,"p1":13.288564996525807,"p2":5.960778941815487},' \
             '{"date":"2020-04-07T13:01:00.715570","forward_time":22,"p1":13.265224639439527,"p2":5.943419193327119},' \
             '{"date":"2020-04-07T13:01:00.715570","forward_time":23,"p1":13.311390944479728,"p2":6.079659024883538},' \
            '{"date":"2020-04-07T13:01:00.715570","forward_time":24,"p1":13.615948485424282,"p2":6.0767498414672785}]\n'
anomaly_data = '[{"cluster":3,"end_date":"2020-04-07T04:55:00","start_date":"2020-04-07T00:15:00"},' \
               '{"cluster":0,"end_date":"2020-04-07T07:25:00","start_date":"2020-04-07T05:40:00"}]\n'


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
    with test_client:
        resp = test_client.post('/history', data={'start_date': '2020-04-01', 'end_date': '2020-04-05'})
        assert resp.status_code == 200
        assert flask.session['start_date'] == datetime.datetime(2020, 4, 1).isoformat()
        assert flask.session['end_date'] == datetime.datetime(2020, 4, 5).isoformat()


def test_anomalies_get(test_client):
    resp = test_client.get('/anomalies')
    assert resp.status_code == 200


def test_anomalies_post(test_client):
    with test_client:
        resp = test_client.post('/anomalies', data={'start_date': '2020-04-01', 'end_date': '2020-04-05'})
        assert resp.status_code == 200
        assert flask.session['start_date'] == datetime.datetime(2020, 4, 1).isoformat()
        assert flask.session['end_date'] == datetime.datetime(2020, 4, 5).isoformat()


def test_graph_sensors(test_client, requests_mock):
    requests_mock.get('http://api:8000/sensor_data',
                      text=sensor_data)
    resp = test_client.get('/graph/sensors')
    assert resp.status_code == 200


def test_graph_aqi(test_client, requests_mock):
    requests_mock.get('http://api:8000/sensor_data',
                      text=sensor_data)
    resp = test_client.get('/graph/aqius')
    assert resp.status_code == 200


def test_graph_forecast(test_client, requests_mock):
    requests_mock.get('http://api:8000/forecast',
                      text=forec_data)
    resp = test_client.get('/graph/forecast')
    assert resp.status_code == 200


def test_graph_anomalies(test_client, requests_mock):
    requests_mock.get('http://api:8000/sensor_data',
                      text=sensor_data)
    requests_mock.get('http://api:8000/anomaly', text=anomaly_data)
    resp = test_client.get('/graph/anomalies')
    assert resp.status_code == 200
