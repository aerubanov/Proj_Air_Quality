import json
import pandas as pd

from src.data.opentopodata import chunks, get_surface_level, add_surface_altitude

test_data = {
    "results": [
        {
            "dataset": "srtm90m",
            "elevation": 45,
            "location": {
                "lat": -43.5,
                "lng": 172.5
            }
        },
        {
            "dataset": "srtm90m",
            "elevation": 402,
            "location": {
                "lat": 27.6,
                "lng": 1.98
            }
        }
    ],
    "status": "OK"
}


def test_chunks():
    test_list = list(range(10))
    ch = [i for i in chunks(test_list, 5)]
    assert len(ch) == 2
    assert len(ch[0]) == len(ch[1]) == 5
    ch = [i for i in chunks(test_list, 6)]
    assert len(ch) == 2
    assert len(ch[0]) == 6
    assert len(ch[1]) == 4


def test_get_surface_level(requests_mock):
    requests_mock.get('https://api.opentopodata.org/v1/srtm30m', text=json.dumps(test_data))
    loc = [(1, 2), (3, 4)]
    result = get_surface_level(loc)
    assert result[(-43.5, 172.5)] == 45
    assert result[(27.6, 1.98)] == 402


def test_add_surface_altitude(monkeypatch):
    def mock(loc):
        return {loc[i]: i for i in range(len(loc))}
    monkeypatch.setattr("src.data.opentopodata.get_surface_level", mock)

    data = pd.DataFrame(data={'lat': [1, 2, 3], 'lon': [1, 2, 3], 'sealevel_alt': [5, 6, 7]})

    result = add_surface_altitude(data)

    assert result.iloc[0].surface_alt == 5
    assert result.iloc[1].surface_alt == 5
    assert result.iloc[2].surface_alt == 5
