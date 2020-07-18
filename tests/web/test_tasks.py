import datetime

from src.web.models.model import Weather, Sensors
import src.web.loader.tasks as tasks


def test_sensor_task_correct_data(monkeypatch, database_session):
    # test data
    p1 = 5.6
    p2 = 7.3
    temp = 20.0
    press = 99270.67
    hum = 68.9

    def mockreturn():
        return {'p1': p1,
                'p2': p2,
                'temp': temp,
                'press': press,
                'hum': hum,
                }, 10

    monkeypatch.setattr('src.web.loader.tasks.load_sensors', mockreturn)

    tasks.sensor_task(database_session)

    row = database_session.query(Sensors).first()
    assert row.p1 == p1
    assert row.p2 == p2
    assert row.temperature == temp
    assert row.pressure == press
    assert row.humidity == hum


def test_sensor_task_incorrect_data(monkeypatch, database_session):
    test_data_correct = {'p1': 5.6,
                         'p2': 7.3,
                         'temp': 20.0,
                         'press': 99270.67,
                         'hum': 20.0,
                         }
    test_data_incorrect = {'p1': -5.6,
                           'p2': -7.3,
                           'temp': 100.0,
                           'press': 500.0,
                           'hum': 110.0,
                           }

    for key in test_data_correct.keys():
        data = test_data_correct.copy()
        data[key] = test_data_incorrect[key]

        def mockreturn():
            return data, 10

        monkeypatch.setattr('src.web.loader.tasks.load_sensors', mockreturn)

        tasks.sensor_task(database_session)
        row = database_session.query(Sensors).first()

        assert row is None


def test_weather_task_correct_data(monkeypatch, database_session):
    # test data
    times = [datetime.datetime(2020, 1, 31), datetime.datetime(2020, 2, 1)]
    prec = ['prec_0', 'prec_1']
    temp = [20.5, 21.0]
    press = [753, 752]
    wind_speed = [1, 2]
    wind_dir = ['Ю', 'С']
    hum = [67.2, 80.1]

    def mockreturn():
        return {
            'date': times,
            'prec': prec,
            'temp': temp,
            'pressure': press,
            'wind_speed': wind_speed,
            'wind_dir': wind_dir,
            'humidity': hum,
        }

    monkeypatch.setattr('src.web.loader.tasks.parse_weather', mockreturn)

    tasks.weather_task(database_session)

    result = database_session.query(Weather)
    result = result.order_by('date')
    i = 0
    for r in result:
        assert r.date == times[i]
        assert r.prec == prec[i]
        assert r.press == press[i]
        assert r.temp == temp[i]
        assert r.wind_speed == wind_speed[i]
        assert r.wind_dir == wind_dir[i]
        assert r.hum == hum[i]
        i += 1


def test_weather_task_incorrect_data(monkeypatch, database_session):
    correct_data = {
        'date': [datetime.datetime(2020, 1, 31), datetime.datetime(2020, 2, 1)],
        'prec': ['prec_0', 'prec_1'],
        'temp': [20.5, 21.0],
        'pressure': [753, 752],
        'wind_speed': [1, 2],
        'wind_dir': ['Ю', 'С'],
        'hum': [67.2, 80.1],
    }
    incorrect_data = {
        'date': [datetime.datetime(2020, 1, 31), datetime.datetime(2020, 2, 1)],
        'prec': ['prec_0', 'prec_1'],
        'temp': [20.5, -100.0],
        'pressure': [753, 900],
        'wind_speed': [1, 55],
        'wind_dir': ['fdf', 'С'],
        'hum': [-1, 80.1],
    }

    for key in correct_data.keys():
        data = correct_data.copy()
        data[key] = incorrect_data[key]

        def mockreturn():
            return data

        monkeypatch.setattr('src.web.loader.tasks.parse_weather', mockreturn)

        tasks.weather_task(database_session)

        result = database_session.query(Weather)
        result = result.order_by('date').first()
        assert result is None
