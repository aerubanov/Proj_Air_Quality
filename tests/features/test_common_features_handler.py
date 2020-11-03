import pandas as pd

from src.features.common_features_handler import configure_prec_amount


def test():
    data_dict = {'prec_amount': [1, 0, 'Осадков нет', 'Следы осадков']}
    data = pd.DataFrame.from_dict(data_dict)

    assert 'Осадков нет' in data['prec_amount'].unique()
    configure_prec_amount(data)

    assert {1., 0.} == set(data['prec_amount'].unique())
