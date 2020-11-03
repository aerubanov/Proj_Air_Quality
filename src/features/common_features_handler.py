import pandas as pd

PREC_AMOUNT = 'prec_amount'


def configure_prec_amount(data: pd.DataFrame):
    data[PREC_AMOUNT] = data.prec_amount.fillna(method='bfill')
    data[PREC_AMOUNT] = data.prec_amount.astype(str)
    data.loc[data[PREC_AMOUNT] == 'Осадков нет', PREC_AMOUNT] = 0
    data.loc[data[PREC_AMOUNT] == 'Следы осадков', PREC_AMOUNT] = 0
    data[PREC_AMOUNT] = data.prec_amount.astype(float)
