import pandas as pd
import numpy as np


def prepare_data(data: pd.DataFrame) -> pd.DataFrame:
    data['P1_filtr_mean'] = data.P1_filtr_mean.interpolate()
    data['P2_filtr_mean'] = data.P2_filtr_mean.interpolate()

    data['pres_meteo'] = data.pres_meteo.fillna(method='bfill')
    data['temp_meteo'] = data.temp_meteo.fillna(method='bfill')
    data['hum_meteo'] = data.hum_meteo.fillna(method='bfill')
    data['pres_meteo'] = data.pres_meteo.interpolate()
    data['hum_meteo'] = data.hum_meteo.interpolate()
    data['temp_meteo'] = data.temp_meteo.interpolate()

    data['humidity_filtr_mean'] = data.humidity_filtr_mean.interpolate()
    data['temperature_filtr_mean'] = data.temperature_filtr_mean.interpolate()

    data['prec_amount'] = data.prec_amount.fillna(method='bfill')
    data['prec_time'] = data.prec_time.fillna(method='bfill')
    data.loc[data.prec_amount == 'Осадков нет', 'prec_amount'] = 0
    data.loc[data.prec_amount == 'Следы осадков', 'prec_amount'] = 0
    data['prec_amount'] = data.prec_amount.astype(float)
    data['prec_time'] = data.prec_time.interpolate()
    data['prec_amount'] = data.prec_amount.interpolate()
    data['wind_direction'] = data.wind_direction.fillna(method='bfill')
    data['wind_speed'] = data.wind_speed.fillna(method='bfill')
    return data


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


def add_features(data: pd.DataFrame, target) -> pd.DataFrame:
    data['day_of_week'] = data.index.dayofweek
    data['hour'] = data.index.hour
    data['sin_day'] = np.sin(2 * np.pi * data.day_of_week / 7)
    data['cos_day'] = np.cos(2 * np.pi * data.day_of_week / 7)
    data['sin_hour'] = np.sin(2 * np.pi * data.hour / 24)
    data['cos_hour'] = np.cos(2 * np.pi * data.hour / 24)

    data['P_diff1'] = data[target].diff(periods=1)
    data['P_diff2'] = data.P_diff1.diff(periods=1)
    data['P_diff3'] = data.P_diff2.diff(periods=1)
    data['t_diff'] = data.temperature_filtr_mean.diff(periods=1)
    data['t_diff1'] = data.t_diff.diff(periods=1)
    data['t_diff2'] = data.t_diff1.diff(periods=1)
    data['h_diff'] = data.humidity_filtr_mean.diff(periods=1)
    data['h_diff1'] = data.h_diff.diff(periods=1)
    data['h_diff2'] = data.h_diff1.diff(periods=1)

    data['wind_direction'] = data.wind_direction.map(wind_dir)
    data["wind_sin"] = np.sin(np.radians(data.wind_direction))
    data["wind_cos"] = np.cos(np.radians(data.wind_direction))
    # typical value in range [-1, 1], so use 2 to indicate missing value
    data['wind_sin'] = data.wind_sin.fillna(value=2)
    data['wind_cos'] = data.wind_cos.fillna(value=2)

    data['temp_diff'] = data.temp_meteo.diff(periods=3)
    data['humidity_diff'] = data.hum_meteo.diff(periods=3)
    data['pressure_diff'] = data.pres_meteo.diff(periods=3)
    data['wind_sin_diff'] = data.wind_sin.diff(periods=3)
    data['wind_cos_diff'] = data.wind_cos.diff(periods=3)
    data['temp_diff3'] = data.temp_meteo.diff(periods=9)
    data['humidity_diff3'] = data.hum_meteo.diff(periods=9)
    data['pressure_diff3'] = data.pres_meteo.diff(periods=9)
    data['wind_sin_diff3'] = data.wind_sin.diff(periods=9)
    data['wind_cos_diff3'] = data.wind_cos.diff(periods=9)
    return data


class DataTransform:

    def __init__(self, train_transform, target_transform, columns, num_columns, target_col):
        self.train_transform = train_transform
        self.target_transform = target_transform
        self.sel_columns = columns
        self.num_columns = num_columns
        self.target_col = target_col

    def fit_transform(self, data):
        data = data[self.sel_columns]
        data = prepare_data(data)
        data['P_original'] = data[self.target_col]
        data[self.num_columns] = self.train_transform.fit_transform(data[self.num_columns])
        data[self.target_col] = self.target_transform.fit_transform(data[[self.target_col]])
        data = add_features(data, target=self.target_col)
        data = data.resample('1H').mean()
        return data

    def transform(self, data):
        data = data[self.sel_columns]
        data = prepare_data(data)
        data['P_original'] = data[self.target_col]
        data[self.num_columns] = self.train_transform.transform(data[self.num_columns])
        data[self.target_col] = self.target_transform.transform(data[[self.target_col]])
        data = add_features(data, target=self.target_col)
        data = data.resample('1H').mean()
        return data
