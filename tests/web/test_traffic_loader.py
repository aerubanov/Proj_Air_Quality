from src.web.loader import trafic_loader


def test_get_traffic_ball(requests_mock):
    with open('tests/web/data/test_map.html', 'r') as html_file:
        html = html_file.read()
        requests_mock.get(trafic_loader.trafic_map_url, text=html)
        requests_mock.get(trafic_loader.trafic_level_url, text='''{"data":{"level":0}}''')
        level = trafic_loader.get_traffic_ball(trafic_loader.trafic_map_url, trafic_loader.trafic_level_url)
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
