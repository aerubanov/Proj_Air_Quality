
class GraphyteReporter:
    params_to_send = ['five', 'day']
    params_names = {'five': 'five_minute', 'day': 'day'}

    def __init__(self, graphyte):
        self.graphyte = graphyte

    def __call__(self, metrics):
        for key in metrics:
            for param in self.params_to_send:
                name = f'{key}_{self.params_names[param]}'
                self.graphyte.send(name, metrics[key][param])
