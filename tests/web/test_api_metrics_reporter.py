from src.web.api.application.metrics_reporter import graphite_reporter


class GraphyteMock:
    def __init__(self):
        self.sended = {}

    def send(self, name, value):
        self.sended[name] = value
        print(name, value)


def test_metrics_sensors(monkeypatch):
    graphyte = GraphyteMock()
    monkeypatch.setattr('src.web.api.application.metrics_reporter.graphyte', graphyte)
    metrics = {'sensors': {'five': 1, 'day': 1}}
    graphite_reporter(metrics)
    sended = graphyte.sended
    assert sended['sensors_five_minute'] == 1
    assert sended['sensors_day'] == 1


def test_metrics_forecast(monkeypatch):
    graphyte = GraphyteMock()
    monkeypatch.setattr('src.web.api.application.metrics_reporter.graphyte', graphyte)
    metrics = {'forecast': {'five': 1, 'day': 1}}
    graphite_reporter(metrics)
    sended = graphyte.sended
    assert sended['forecast_five_minute'] == 1
    assert sended['forecast_day'] == 1


def test_metrics_anomalies(monkeypatch):
    graphyte = GraphyteMock()
    monkeypatch.setattr('src.web.api.application.metrics_reporter.graphyte', graphyte)
    metrics = {'anomalies': {'five': 1, 'day': 1}}
    graphite_reporter(metrics)
    sended = graphyte.sended
    assert sended['anomalies_five_minute'] == 1
    assert sended['anomalies_day'] == 1


def test_metrics_status_200(monkeypatch):
    graphyte = GraphyteMock()
    monkeypatch.setattr('src.web.api.application.metrics_reporter.graphyte', graphyte)
    metrics = {'status_200': {'five': 1, 'day': 1}}
    graphite_reporter(metrics)
    sended = graphyte.sended
    assert sended['status_200_five_minute'] == 1
    assert sended['status_200_day'] == 1


def test_metrics_status_400(monkeypatch):
    graphyte = GraphyteMock()
    monkeypatch.setattr('src.web.api.application.metrics_reporter.graphyte', graphyte)
    metrics = {'status_400': {'five': 1, 'day': 1}}
    graphite_reporter(metrics)
    sended = graphyte.sended
    assert sended['status_400_five_minute'] == 1
    assert sended['status_400_day'] == 1


def test_metrics_status_404(monkeypatch):
    graphyte = GraphyteMock()
    monkeypatch.setattr('src.web.api.application.metrics_reporter.graphyte', graphyte)
    metrics = {'status_404': {'five': 1, 'day': 1}}
    graphite_reporter(metrics)
    sended = graphyte.sended
    assert sended['status_404_five_minute'] == 1
    assert sended['status_404_day'] == 1
