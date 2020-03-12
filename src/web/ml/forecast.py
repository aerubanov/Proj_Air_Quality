import datetime
import pandas as pd
import pickle

from src.web.models.model import Sensors, Forecast
from src.model.forecast import ForecastModel

p1_file = "models/p1_forecast.obj"
p2_file = "models/p2_forecast.obj"


def perform_forecast(session, date=None, logger=None):
    """make forecast for date + 24 hours and write it in database"""
    if date is None:
        date = datetime.datetime.utcnow()
    result = session.query(Sensors).filter(Sensors.date >= date - datetime.timedelta(days=1))
    result = [i.serialize for i in result]
    data = pd.DataFrame(result)
    data = data.rename(columns={'p1': 'P1', 'p2': 'P2'})
    data['date'] = pd.to_datetime(data.date)
    with open(p1_file, 'rb') as p1_f, open(p2_file, 'rb') as p2_f:
        p1_models = pickle.load(p1_f)
        p2_models = pickle.load(p2_f)
        model = ForecastModel(p1_models, p2_models)
        p1_predictions, p2_predictions = model.predict(data)
        for i in range(len(p1_predictions)):
            forec = Forecast(date=date, p1=p1_predictions[i],
                             p2=p2_predictions[i], forward_time=i + 1)
            session.add(forec)
            session.commit()
        if logger is not None:
            logger.info(f'Make forecast update')
