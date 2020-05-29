sensor_file = 'DATA/processed/sensors.csv'  # file with information about sensors to data downloading
api_url = 'https://data.sensor.community/static/v2/data.json'
sensor_time_interval = 5  # interval for api requests in minutes

weather_url = 'https://rp5.ru/%D0%9F%D0%BE%D0%B3%D0%BE%D0%B4%D0%B0_%D0%B2_%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D0%B5' \
      '_(%D1%86%D0%B5%D0%BD%D1%82%D1%80,_%D0%91%D0%B0%D0%BB%D1%87%D1%83%D0%B3)'
weather_time_interval = 60  # interval for weather forecast requests in minutes

mosecom_url = 'https://mosecom.mos.ru/wp-content/themes/moseco/map/stations-new.php'

trafic_map_url = 'https://yandex.ru/maps/213/moscow/?l=trf%2Ctrfe&ll=37.622504%2C55.753215&z=10'
trafic_level_url = 'https://yandex.ru/maps/api/traffic/getLevelInfo?ajax=1&'
