import graphyte

from src.web.config import metrics_host

graphyte.init(metrics_host, prefix='api')


def graphite_reporter(metrics):
    if 'sensors' in metrics:
        graphyte.send('senors_five_minute', metrics['sensors']['five'])
        graphyte.send('senors_day', metrics['sensors']['day'])
    if 'forecast' in metrics:
        graphyte.send('forecast_five_minute', metrics['forecast']['five'])
        graphyte.send('forecast_day', metrics['forecast']['day'])
    if 'anomalies' in metrics:
        graphyte.send('forecast_five_minute', metrics['anomalies']['five'])
        graphyte.send('forecast_day', metrics['anomalies']['day'])
