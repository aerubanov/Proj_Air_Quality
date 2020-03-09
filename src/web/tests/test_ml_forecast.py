import datetime
import pandas as pd

from src.web.ml.forecast import perform_forecast
from src.web.models.model import Forecast

test_data = 'src/web/tests/data/test_dataset_2.csv'


def test_perform_forecast(database_session):
    data = pd.read_csv(test_data, parse_dates=['date'])
    data = data.set_index('date')
    engine = database_session.get_bind()
    data.to_sql('sensors', con=engine, if_exists='append')
    date = data.index[-1].to_pydatetime()
    perform_forecast(database_session, date)
    res = database_session.query(Forecast).filter(Forecast.date == date).all()
    assert len(res) == 24
