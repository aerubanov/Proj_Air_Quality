import pandas as pd
import numpy as np


def prepare_meteo_data(data, columns):
    for c in columns:
        data[c].fillna(method='bfill', inplace=True)
    return data


def prepare_sensors_data(data, columns):
    for c in columns:
        data[c].interpolate(inplace=True)
        data[c].fillna(data[c].mean(), inplace=True)
    return data


# matching wind direction and angle
wind_dir = {'Ветер, дующий с востока': 0,
            'Ветер, дующий с востоко-северо-востока': 45 / 2,
            'Ветер, дующий с северо-востока': 45,
            'Ветер, дующий с северо-северо-востока': 45 + 45 / 2,
            'Ветер, дующий с севера': 90,
            'Ветер, дующий с северо-северо-запад': 90 + 45 / 2,
            'Ветер, дующий с северо-запада': 135,
            'Ветер, дующий с западо-северо-запада': 135 + 45 / 2,
            'Ветер, дующий с запада': 180,
            'Ветер, дующий с западо-юго-запада': 180 + 45 / 2,
            'Ветер, дующий с юго-запада': 225,
            'Ветер, дующий с юго-юго-запада': 225 + 45 / 2,
            'Ветер, дующий с юга': 270,
            'Ветер, дующий с юго-юго-востока': 270 + 45 / 2,
            'Ветер, дующий с юго-востока': 315,
            'Ветер, дующий с востоко-юго-востока': 315 + 45 / 2,
            'Штиль, безветрие': None,
            }


def add_features(data: pd.DataFrame) -> pd.DataFrame:
    """Features preparation for anomaly detection and clustering"""

    data['wind_direction'] = data.wind_direction.fillna(method='bfill')
    data['wind_direction'] = data.wind_direction.map(wind_dir)

    data['prec_amount'] = data.prec_amount.fillna(method='bfill')
    data.loc[data.prec_amount == 'Осадков нет', 'prec_amount'] = 0
    data.loc[data.prec_amount == 'Следы осадков', 'prec_amount'] = 0
    data['prec_amount'] = data.prec_amount.astype(float)
    data['prec_time'] = data.prec_time.fillna(method='bfill')
    data['prec_amount'] = data.prec_amount / data.prec_time

    data['dew_point_diff'] = data.temp_meteo - data.dew_point_temp

    # data['P1_iqr_25_75'] = data.P1_p75 - data.P1_p25
    # data['P1_iqr_10_90'] = data.P1_p90 - data.P1_p10

    # data['P2_iqr_25_75'] = data.P2_p75 - data.P2_p25
    # data['P2_iqr_10_90'] = data.P2_p90 - data.P2_p10

    # data['temp_iqr_25_75'] = data.temperature_p75 - data.temperature_p25
    # data['temp_iqr_10_90'] = data.temperature_p90 - data.temperature_p10

    # data['hum_iqr_25_75'] = data.humidity_p75 - data.humidity_p25
    # data['hum_iqr_10_90'] = data.humidity_p90 - data.humidity_p10

    data["wind_sin"] = np.sin(np.radians(data.wind_direction))
    data["wind_cos"] = np.cos(np.radians(data.wind_direction))
    data['wind_sin'] = data.wind_sin.fillna(value=2)
    data['wind_cos'] = data.wind_cos.fillna(value=2)

    return data
