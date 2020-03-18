from sqlalchemy import Column, DateTime, Float, String, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Sensors(Base):
    __tablename__ = 'sensors'

    date = Column(DateTime, primary_key=True)
    p1 = Column(Float)
    p2 = Column(Float)
    temperature = Column(Float)
    humidity = Column(Float)
    pressure = Column(Float)

    def __repr__(self):
        return f'date: {self.date}|P1: {self.p1}|P2: {self.p2}|temp: {self.temperature}|hum:' \
               f' {self.humidity}|press: {self.pressure}'

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'date': self.date.isoformat('T'),
            'p1': self.p1,
            'p2': self.p2,
            'temperature': self.temperature,
            'humidity': self.humidity,
            'pressure': self.pressure,
        }


class Weather(Base):
    __tablename__ = "weather"

    date = Column(DateTime, primary_key=True)
    temp = Column(Float)
    press = Column(Float)
    prec = Column(String)
    wind_speed = Column(Float)
    wind_dir = Column(String)
    hum = Column(Float)

    def __repr__(self):
        return f'date: {self.date}|temp: {self.temp}|press: {self.press}|prec: {self.prec}|' \
               f'wind_speed: {self.wind_speed}|wind_dir: {self.wind_dir}|hum: {self.hum}'

    @property
    def serialize(self):
        return{
            'date': self.date.isoformat('T'),
            'temp': self.temp,
            'press': self.press,
            'prec': self.prec,
            'wind_speed': self.wind_speed,
            'wind_dir': self.wind_dir,
            'hum': self.hum,
        }


class Anomaly(Base):
    __tablename__ = 'anomalies'

    start_date = Column(DateTime, primary_key=True)
    end_date = Column(DateTime)
    cluster = Column(Integer)

    @property
    def serialize(self):
        return {
            'start_date': self.start_date.isoformat('T'),
            'end_date': self.end_date.isoformat('T'),
            'cluster': self.cluster,
        }


class Forecast(Base):
    __tablename__ = 'forecasts'

    date = Column(DateTime, primary_key=True)
    p1 = Column(Float)
    p2 = Column(Float)
    forward_time = Column(Integer, primary_key=True)

    @property
    def serialize(self):
        return {
            'date': self.date.isoformat('T'),
            'p1': self.p1,
            'p2': self.p2,
            'forward_time': self.forward_time,
        }

    def __repr__(self):
        return f'date: {self.date}|forward: {self.forward_time}|p1: {self.p1}|p2: {self.p2}'


class LoaderLog(Base):
    __tablename__ = 'loader_logs'

    date = Column(DateTime, primary_key=True)
    level = Column(String)
    name = Column(String)
    message = Column(String)

    def __repr__(self):
        return f'date: {self.date}| level: {self.level}|name: {self.name}|message: {self.message}'
