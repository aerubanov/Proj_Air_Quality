[![Build Status](https://travis-ci.org/aerubanov/DS_for_Air.svg?branch=master)](https://travis-ci.org/aerubanov/DS_for_Air)
# DS_for_Air
Проект по использованию Data Scince для анализа качества воздуха в Москве и (в перспективе) предсказания его измения. 

## Источник данных
В проекте используются проекта данные общественного мониторнга воздуха проекта
[Luftdaten](https://luftdaten.info/ "luftdaten.info"). Данные собираются с датчиков концентрации частиц, температуры, атмосферного
давления и влажности воздуха и размещаются в открытом доступе. В Москве установкой станций мониторинга качества воздуха занимаются
волонтеры [breathe.moscov](https://breathe.moscow/ "breathe.moscow").

Информация о погоде в Москве используется по данным метеостанции [Балчуг](https://rp5.ru/%D0%90%D1%80%D1%85%D0%B8%D0%B2_%D0%BF%D0%BE%D0%B3%D0%BE%D0%B4%D1%8B_%D0%B2_%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D0%B5_(%D1%86%D0%B5%D0%BD%D1%82%D1%80,_%D0%91%D0%B0%D0%BB%D1%87%D1%83%D0%B3\) "rp5.ru")  

Для храния данных в проекте используется [Data Version Control](https://dvc.org/ "Open-source Version Control System
for Machine Learning Projects"). Для получения данных после клонирования репозитория выполните
```
pip install dvc
```
для загрузки данных с датчиков выполните
```
dvc repro dvs_stages/update_data.dvc
```
для загрузки даных погоды с метеостанции выполните
```
dvc repro dvc_stages/update_wather.dvc
```
Начальная дата для скачивания данных задается параметром DEFAULT_DATE в 
файлах [update_data.py](src/data/update_data.py) и [update_wather.py](src/data/update_wather.py)
Скачанные данные будут храниться в DATA/raw/sensors и DATA/raw/wather соответсвтенно. При повторном
 запуске команд будут подгружены новые данные за прошедший промежуток времени без повторного скачивания. 


## Docs
### raw
[raw_data.rst](docs/data/raw_data.rst)
### processed
[dataset.rst](docs/data/dataset.rst)
### dvc-pipleine
update_wather --------------------------->|

update_sensor_id -> update_data ->| -> create_dataset -> train_clustering

## Notebooks
Выделение и кластеризация аномалий в данных
 
 [Anomaly detection.ipynb](notebooks/Anomaly%20detection.ipynb)