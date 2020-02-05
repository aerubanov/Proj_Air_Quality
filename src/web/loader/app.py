from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import time
import schedule
import datetime

from src.web.models.model import Base, Sensors, Weather
from src.web.loader.sensor_loading import read_sensor_id, load_data, average_data
from src.web.loader.config import sensor_file, sensor_time_interval


def sensor_task(session):
    sensor_id = read_sensor_id(sensor_file)
    data = load_data(sensor_id)
    avg_data = average_data(data)
    row = Sensors(date=datetime.datetime.now(), p1=avg_data['p1'], p2=avg_data['p1'], temperature=avg_data['temp'],
                  humidity=avg_data['hum'], pressure=avg_data['press'])
    session.add(row)
    session.commit()


def print_db(session):
    result = session.query(Sensors)
    result = result.order_by('date')
    print("date | p1 | p2| temp| press | hum", flush=True)
    for i in result:
        print(f'{i.date} | {i.p1} | {i.p2} | {i.temperature} | {i.pressure} | {i.humidity}', flush=True)


if __name__ == '__main__':
    import os
    cwd = os.getcwd()
    time.sleep(5)  # wait postgres image loading
    engine = create_engine('postgresql://postgres:postgres@PostgreSQL/pgdb')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    sess = Session()
    schedule.every(sensor_time_interval).minutes.do(sensor_task, session=sess)
    schedule.every(20).seconds.do(print_db, session=sess)

    while True:
        schedule.run_pending()
        time.sleep(1)
