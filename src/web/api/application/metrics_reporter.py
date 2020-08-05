import graphyte

from src.web.config import metrics_host

graphyte.init(metrics_host, prefix='api')


def graphite_reporter(metrics):
    if 'sensors' in metrics:
        graphyte.send('sensors_five_minute', metrics['sensors']['five'])
        graphyte.send('sensors_day', metrics['sensors']['day'])
    if 'forecast' in metrics:
        graphyte.send('forecast_five_minute', metrics['forecast']['five'])
        graphyte.send('forecast_day', metrics['forecast']['day'])
    if 'anomalies' in metrics:
        graphyte.send('anomalies_five_minute', metrics['anomalies']['five'])
        graphyte.send('anomalies_day', metrics['anomalies']['day'])
    if "status_200" in metrics:
        graphyte.send('status_200_five_minute', metrics['status_200']['five'])
        graphyte.send('status_200_day', metrics['status_200']['day'])
    if "status_400" in metrics:
        graphyte.send('status_400_five_minute', metrics['status_400']['five'])
        graphyte.send('status_400_day', metrics['status_400']['day'])
    if "status_404" in metrics:
        graphyte.send('status_404_five_minute', metrics['status_404']['five'])
        graphyte.send('status_404_day', metrics['status_404']['day'])
