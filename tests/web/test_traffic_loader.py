from src.web.loader import trafic_loader


def test_get_traffic_ball(requests_mock):
    with open('tests/web/data/test_map.html', 'r') as html_file:
        html = html_file.read()
        requests_mock.get('http:://map/', text=html)
        requests_mock.get('http:://level/', text='''{"data":{"level":0}}''')
        level = trafic_loader.get_traffic_ball('http://map.com', 'http://level.com')
        assert level == 0


def test_load_traffic_level(monkeypatch, tmpdir):
    d = tmpdir.mkdir('test/')
    file = d.join('traffic_level.csv')

    def mockreturn(url1, url2):
        return 1
    monkeypatch.setattr('src.web.loader.trafic_loader.get_traffic_ball', mockreturn)
    monkeypatch.setattr('src.web.loader.trafic_loader.DATA_PATH', file)

    trafic_loader.load_traffic_level()

    assert len(file.read().splitlines()) == 1
