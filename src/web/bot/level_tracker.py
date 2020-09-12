import requests
import datetime
import json
from abc import ABC, abstractmethod

from src.web.bot.config import API_HOST, ANOMALY_LOOK_UP_INTERVAL, FORECAST_LOOK_UP_INTERVAL
from src.web.utils.aqi import aqi_level, pm25_to_aqius


class LevelTracker(ABC):
    def __init__(self, callback):
        self.previous_level = None
        # to prevent user notification here firstly set callback None
        self.callback = None
        self.check()
        # and now set actual callback value
        self.callback = callback

    @abstractmethod
    def check(self):
        # check value change hear
        # if value changed, call self.callback()and
        # update self.previous_level if needed
        pass


class ConcentrationTracker(LevelTracker):
    def check(self):
        start_date = datetime.datetime.utcnow() - datetime.timedelta(hours=6)
        end_date = datetime.datetime.utcnow()
        r = requests.get(API_HOST + '/sensor_data',
                         json={"end_time": end_date.isoformat('T'),
                               "start_time": start_date.isoformat('T'),
                               "columns": ['p1']}
                         )
        data = json.loads(r.text)
        p1 = data[-1]['p1']
        aqi = pm25_to_aqius(p1)
        level = aqi_level(aqi)
        if level != self.previous_level:
            self.previous_level = level
            if self.callback is not None:
                self.callback(event_type='concentration', aqi_level=level)


class AnomaliesTracker(LevelTracker):
    def check(self):
        end_date = datetime.datetime.utcnow()
        start_date = end_date - datetime.timedelta(hours=ANOMALY_LOOK_UP_INTERVAL)
        r = requests.get(API_HOST + '/anomaly',
                         json={"end_time": end_date.isoformat('T'),
                               "start_time": start_date.isoformat('T'),
                               }
                         )
        data = json.loads(r.text)
        cluster = data[0]['cluster'] if data else None
        if cluster != self.previous_level:
            self.previous_level = cluster
            if self.callback is not None:
                self.callback(event_type='anomalies', cluster=cluster)


class ForecastTracker(LevelTracker):
    def check(self):
        r = requests.get(API_HOST + '/forecast', json={})
        data = json.loads(r.text)
        data = [{'date': datetime.datetime.fromisoformat(item['date']) + datetime.timedelta(hours=item['forward_time']),
                 'p1': item['p1']} for item in data]
        start_date = datetime.datetime.utcnow()
        end_date = start_date + datetime.timedelta(hours=FORECAST_LOOK_UP_INTERVAL)
        data = [item['p1'] for item in data if start_date <= item['date'] <= end_date]
        if data:
            p1 = max(data)
            aqi = pm25_to_aqius(p1)
            level = aqi_level(aqi)
            if level != self.previous_level:
                self.previous_level = level
                if self.callback is not None:
                    self.callback(event_type='forecast', aqi_level=level)
