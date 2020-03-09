import pandas as pd
import datetime
import numpy as np
from typing import List


def prepare_features(data: pd.DataFrame) -> pd.DataFrame:
    """Features preparation for anomaly detection and clustering"""
    # fill missing value
    for c in data.columns:
        data[c].fillna((data[c].mean()), inplace=True)

    return data


def pp(start: datetime.datetime, end: datetime.datetime, n: int) -> pd.DatetimeIndex:
    """ generate random n datetime from [start, end] interval"""
    start_u = start.value//10**9
    end_u = end.value//10**9

    return pd.DatetimeIndex((10**9*np.random.randint(start_u, end_u, n)).view('M8[ns]'))


def generate_chunks(series: pd.DataFrame, n: int, start: datetime.datetime, end: datetime.datetime):
    """split time-series by chunks"""
    chanks = []
    for idx in pp(start, end, n):
        c = series[str(idx):str(idx+datetime.timedelta(days=2))]
        chanks.append(c)
    return chanks


def create_sample(chunk: pd.DataFrame, target_col: str, columns: List[str]):
    """extract features from chunks"""
    x = dict()
    y = dict()
    d1 = chunk.iloc[:24]
    d2 = chunk.iloc[24:]
    for i in range(24):
        for c in columns:
            x[f'{c}_lag_{i}'] = d1[target_col][-(i+1)]
        y[f'{target_col}_forec_{i}'] = d2[target_col][i]
    return x, y


def prepare_data_from_chunks(chunks: List[pd.DataFrame], target: str, col: List[str]):
    """generate dataframe from chunks"""
    df = pd.DataFrame(index=range(len(chunks)))
    for i in range(len(chunks)):
        x, y = create_sample(chunks[i], target, col)
        for key, value in x.items():
            df.loc[i, key] = value
        for key, value in y.items():
            df.loc[i, key] = value
    return df


def prepare_test_sample(chunk, columns, target_col='P1'):
    d1 = chunk.iloc[:24]
    x = pd.DataFrame(index=range(1))
    for i in range(24):
        for c in columns:
            x[f'{c}_lag_{i}'] = d1[target_col][-(i + 1)]
    return x
