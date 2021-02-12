import json
import requests
import typing
import pandas as pd


def chunks(lst, n):
    """Yield successive n-sized chunks from lst.
    See details https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks"""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def get_surface_level(locations: typing.List[typing.Tuple]) -> typing.Dict[typing.Tuple, float]:
    """get surface level altitude from srtm30m dataset.
     See details https://www.opentopodata.org/api/"""
    result = dict()
    for chunk in chunks(locations, 100):
        payload = '|'.join([f'{lat},{lon}' for lat, lon in chunk])
        resp = requests.get(f'https://api.opentopodata.org/v1/srtm30m?locations={payload}')
        data = json.loads(resp.text)
        for item in data['results']:
            result[(item["location"]['lat'], item["location"]['lng'])] = item["elevation"]
    return result


def add_surface_altitude(sensors: pd.DataFrame) -> pd.DataFrame:
    """add surfac_alt column based on lat, lon and sealevel_alt"""
    lat, lon = sensors.lat.values, sensors.lon.values
    locations = [(lat[i], lon[i]) for i in range(len(sensors))]
    levels = get_surface_level(locations)
    levels = [levels[item] for item in locations]
    sensors['surface_alt'] = levels
    sensors['surface_alt'] = sensors['sealevel_alt'] - sensors['surface_alt']
    return sensors
