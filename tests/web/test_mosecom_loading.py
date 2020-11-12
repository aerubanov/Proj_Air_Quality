import os
import numpy as np

from src.web.server.loader.application.mosecom_loading import load_data, write_raw_data, write_processed, avarege_data
from src.web.server.loader.config import mosecom_url


def test_load_data(requests_mock):
    requests_mock.post(mosecom_url,
                       text='''{"able": [{"item1": "1"}, {"item2": "2"}], "other": []}''')
    data1, data2 = load_data()
    print(data1)
    assert data1 == [{'item1': '1'}, {'item2': '2'}]
    assert data2 == [{'item1': '1'}, {'item2': '2'}]


def test_write_raw(tmpdir, monkeypatch):
    processed_path = 'processed/'
    raw_path = 'raw/'
    d1 = tmpdir.mkdir(processed_path)
    d2 = tmpdir.mkdir(raw_path)

    data = [{'stationname': 'Сухаревская площадь',
             'name': 'Сухаревская площадь',
             'stationId': 'Сухаревская площадь',
             'full_name': 'Сухаревская площадь',
             'address': 'Малая Сухаревская площадь, дом 1 строение 1',
             'pageLink': '/suxarevskaya-ploshhad/',
             'latitude': 55.773757,
             'longitude': 37.627445,
             'modifyav': 0.007,
             'unit': 'мг/м3',
             'pdkcolor': 'green',
             'pdk': 0.0444,
             'norma': 0.16,
             'norma_2': 0.8},
            {'stationname': 'МКАД 52 запад',
             'name': 'МКАД 52 запад',
             'stationId': 'МКАД 52 запад',
             'full_name': 'МКАД 52 км (запад)',
             'address': 'МКАД, 52-й километр, дом 8',
             'pageLink': '/mkad-52-km-zapad/',
             'latitude': 55.703489,
             'longitude': 37.397577,
             'modifyav': 0,
             'unit': 'мг/м3',
             'pdkcolor': 'green',
             'pdk': 0.0008,
             'norma': 0.16,
             'norma_2': 0.8}]
    f1 = d1.join('mosecom_station.csv')
    f1.write('''station_name,lon,lat, type\nСухаревская площадь,37.627445,55.773757,P1\n''')

    f2 = d2.join('Сухаревская площадьP1.csv')
    f2.write('''date,pdk,norma\n2020-04-21T11:56:06.743291,0.0352,0.16\n''')

    monkeypatch.setattr('src.web.server.loader.application.mosecom_loading.raw_path', d2)
    monkeypatch.setattr('src.web.server.loader.application.mosecom_loading.processed_path', d1)

    write_raw_data(data, 'P1')

    assert len(f1.read().splitlines()) == 3
    assert len(f1.read().splitlines()) == 3
    assert len(os.listdir(d2)) == 2
    with open(os.path.join(d2, 'МКАД 52 западP1.csv'), 'r') as f:
        assert len(f.read().splitlines()) == 2


def test_avarege_data():
    data = [{'stationname': 'Народного ополчения',
             'name': 'Народного ополчения',
             'stationId': 'Народного ополчения',
             'full_name': 'Народного ополчения',
             'address': 'Улица Народного Ополчения, дом 21, корпус 1',
             'pageLink': '/narodnogo-opolcheniya/',
             'latitude': 55.776064,
             'longitude': 37.475878,
             'modifyav': 0,
             'unit': 'мг/м3',
             'pdkcolor': 'green',
             'pdk': 0,
             'norma': 0.16,
             'norma_2': 0.8},
            {'stationname': 'Сухаревская площадь',
             'name': 'Сухаревская площадь',
             'stationId': 'Сухаревская площадь',
             'full_name': 'Сухаревская площадь',
             'address': 'Малая Сухаревская площадь, дом 1 строение 1',
             'pageLink': '/suxarevskaya-ploshhad/',
             'latitude': 55.773757,
             'longitude': 37.627445,
             'modifyav': 0.007,
             'unit': 'мг/м3',
             'pdkcolor': 'green',
             'pdk': 0.0444,
             'norma': 0.16,
             'norma_2': 0.8},
            {'stationname': 'МКАД 52 запад',
             'name': 'МКАД 52 запад',
             'stationId': 'МКАД 52 запад',
             'full_name': 'МКАД 52 км (запад)',
             'address': 'МКАД, 52-й километр, дом 8',
             'pageLink': '/mkad-52-km-zapad/',
             'latitude': 55.703489,
             'longitude': 37.397577,
             'modifyav': 0,
             'unit': 'мг/м3',
             'pdkcolor': 'green',
             'pdk': 0.0008,
             'norma': 0.16,
             'norma_2': 0.8}]

    stat = avarege_data(data)
    values = [i['pdk'] * i['norma'] * 1000 for i in data]
    assert stat['len'] == 3
    assert np.isclose(stat['p10'], np.percentile(values, q=10))
    assert np.isclose(stat['p25'], np.percentile(values, q=25))
    assert np.isclose(stat['p50'], np.percentile(values, q=50))
    assert np.isclose(stat['p75'], np.percentile(values, q=75))
    assert np.isclose(stat['p90'], np.percentile(values, q=90))


def test_write_processed(tmpdir, monkeypatch):
    d = tmpdir.mkdir('processed')
    f = d.join('mosecom_moscow_pm.csv')
    f.write('''ts,mosecom_pm10_count,mosecom_pm10_p10,mosecom_pm10_p25,mosecom_pm10_p50,mosecom_pm10_p75,'''
            '''mosecom_pm10_p90,mosecom_pm25_count,mosecom_pm25_p10,mosecom_pm25_p25,mosecom_pm25_p50,'''
            '''mosecom_pm25_p75,mosecom_pm25_p90\n'''
            '''"2019-10-28 22:00:00","16","3","11.5","13","16.5","25","8",'''
            '''"0.699999988079071","2.5","5","5.5","7.900000095367432"\n''')

    data = [{'stationname': 'Народного ополчения',
             'name': 'Народного ополчения',
             'stationId': 'Народного ополчения',
             'full_name': 'Народного ополчения',
             'address': 'Улица Народного Ополчения, дом 21, корпус 1',
             'pageLink': '/narodnogo-opolcheniya/',
             'latitude': 55.776064,
             'longitude': 37.475878,
             'modifyav': 0,
             'unit': 'мг/м3',
             'pdkcolor': 'green',
             'pdk': 0,
             'norma': 0.16,
             'norma_2': 0.8},
            ]

    def mockreturn(data):
        return {
            'p10': 1,
            'p25': 2,
            'p50': 3,
            'p75': 4,
            'p90': 4,
            'len': 3,
        }

    monkeypatch.setattr('src.web.server.loader.application.mosecom_loading.processed_path', d)
    monkeypatch.setattr('src.web.server.loader.application.mosecom_loading.avarege_data', mockreturn)

    write_processed(data, data)

    assert len(f.read().splitlines()) == 3
