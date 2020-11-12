from src.web.server.loader import TrafficLoader


def test_prepare_api_call(requests_mock):
    traffic_loader = TrafficLoader()
    with open('tests/web/data/test_map.html', 'r') as html_file:
        html = html_file.read()
        requests_mock.get('http://map.com/', text=html)
        traffic_loader._TrafficLoader__prepare_api_call('http://map.com')

        assert traffic_loader._TrafficLoader__sess_id == '1590781973521_980315'
        assert traffic_loader._TrafficLoader__token == '6529f0f337bd1c160b81f4f54434845f24f62c2a:1590781973'


def test_load_traffic_level(requests_mock):
    traffic_loader = TrafficLoader()
    requests_mock.get('http://level.com/', text='{"data": {"level": 0}}')
    traffic_loader._TrafficLoader__load_traffic_level('http://level.com/')
    assert traffic_loader._TrafficLoader__level == 0


def test_write_wrong_traffic_level():
    traffic_loader = TrafficLoader()
    traffic_loader._TrafficLoader__level = -1
    is_success = traffic_loader._TrafficLoader__write_traffic_level()
    assert is_success is False


def test_write_proper_traffic_level(monkeypatch, tmpdir):
    d = tmpdir.mkdir('test/')
    file = d.join('traffic_level.csv')
    monkeypatch.setattr('src.web.loader.traffic_loader.DATA_PATH', file)

    traffic_loader = TrafficLoader()
    traffic_loader._TrafficLoader__level = 1
    is_success = traffic_loader._TrafficLoader__write_traffic_level()

    assert is_success is True
    assert len(file.read().splitlines()) == 1
