import datetime
import math

from src.web.scripts import fill_database
from src.web.models.model import Sensors


def test_load_data():
    data = fill_database.load_data('src/web/tests/data/test_dataset_1.csv')
    assert data.index[0].to_pydatetime() == datetime.datetime(2019, 4, 1, 3, 0)
    assert math.isclose(data.p1[0], 6.647142857142856, rel_tol=1e-09)
    assert math.isclose(data.p2[0], 2.8817857142857144, rel_tol=1e-09)
    assert math.isclose(data.temperature[0], 4.99125, rel_tol=1e-09)
    assert math.isclose(data.humidity[0], 58.79375, rel_tol=1e-09)
    assert math.isclose(data.pressure[0], 98722.855, rel_tol=1e-09)


def test_last_date():
    data = fill_database.load_data('src/web/tests/data/test_dataset_1.csv')
    last_date = fill_database.get_last_date(data)
    assert last_date == datetime.datetime(2019, 4, 1, 3, 10)


def test_clear_database(database_session):
    end_date = datetime.datetime(2020, 2, 24, 3, 7, 15)

    entr_1 = Sensors(date=end_date-datetime.timedelta(minutes=5))
    entr_2 = Sensors(date=end_date)
    entr_3 = Sensors(date=end_date + datetime.timedelta(minutes=5))
    database_session.add(entr_1)
    database_session.add(entr_2)
    database_session.add(entr_3)
    database_session.commit()

    fill_database.clear_database(end_date, database_session)
    q = database_session.query(Sensors).all()
    dates = [i.date for i in q]
    assert dates == [end_date + datetime.timedelta(minutes=5)]


def test_write_data(database_session):
    entry = Sensors(date=datetime.datetime(2020, 2, 20))
    database_session.add(entry)
    database_session.commit()
    data = fill_database.load_data('src/web/tests/data/test_dataset_1.csv')
    fill_database.write_data(data, database_session)
    res = database_session.query(Sensors).all()
    assert len(res) == len(data) + 1
