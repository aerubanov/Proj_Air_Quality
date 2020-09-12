import datetime

from src.web.bot.level_tracker import ConcentrationTracker, ForecastTracker, AnomaliesTracker
from src.web.bot.config import API_HOST


class TestCallback:
    def __init__(self):
        self.kw = {}

    def __call__(self, **kwargs):
        self.kw = kwargs


def test_concentration_tracker(requests_mock):
    cb = TestCallback()
    requests_mock.get(API_HOST + '/sensor_data', text='[{"p1":3.5600970873786406},{"p1":2.733960396039604}]\n')
    conc_tr = ConcentrationTracker(cb)
    requests_mock.get(API_HOST + '/sensor_data', text='[{"p1":3.5600970873786406},{"p1":30.733960396039604}]\n')
    conc_tr.check()
    assert cb.kw['event_type'] == 'concentration'
    assert cb.kw['aqi_level'] == 'Moderate'


def test_anomalies_tracker(requests_mock):
    cb = TestCallback()
    requests_mock.get(API_HOST + '/anomaly', text='[]\n')
    anom_tr = AnomaliesTracker(cb)
    requests_mock.get(API_HOST + '/anomaly', text='[{"cluster":0,"end_date":"2020-04-07T07:25:00",'
                                                  '"start_date":"2020-04-07T05:40:00"}]\n')
    anom_tr.check()
    assert cb.kw['event_type'] == 'anomalies'
    assert cb.kw['cluster'] == 0


def test_forecast_tracker(requests_mock):
    cb = TestCallback()
    date = datetime.datetime.utcnow()
    requests_mock.get(API_HOST + '/forecast', text=f'[{{"date":"{date.isoformat("""T""")}",'
                                                   f'"forward_time":1,"p1":3.10}},'
                                                   f'{{"date":"{date.isoformat("""T""")}",'
                                                   f'"forward_time":2,"p1":4.0}}]\n')
    forec_tr = ForecastTracker(cb)
    requests_mock.get(API_HOST + '/forecast', text=f'[{{"date":"{date.isoformat("""T""")}",'
                                                   f'"forward_time":1,"p1":3.10}},'
                                                   f'{{"date":"{date.isoformat("""T""")}",'
                                                   f'"forward_time":2,"p1":30.10}}]\n')
    forec_tr.check()
    assert cb.kw['event_type'] == 'forecast'
    assert cb.kw['aqi_level'] == 'Moderate'
