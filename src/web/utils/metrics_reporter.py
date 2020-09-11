
class GraphyteReporter:
    params_to_send = ['five', 'day']
    meter_params_names = {'five': 'five_minute', 'day': 'day'}

    def __init__(self, graphyte):
        self.graphyte = graphyte

    def __call__(self, metrics):
        for key in metrics:
            if metrics[key]['kind'] == 'meter':
                for param in self.meter_params_names:
                    name = f'{key}_{self.meter_params_names[param]}'
                    self.graphyte.send(name, metrics[key][param])
            if metrics[key]['kind'] == 'counter':
                self.graphyte.send(key, metrics[key]['value'])
