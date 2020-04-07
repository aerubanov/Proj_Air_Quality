[![Build Status](https://travis-ci.org/aerubanov/DS_for_Air.svg?branch=master)](https://travis-ci.org/aerubanov/DS_for_Air)
[![codecov](https://codecov.io/gh/aerubanov/DS_for_Air/branch/master/graph/badge.svg)](https://codecov.io/gh/aerubanov/DS_for_Air)
# DS_for_Air
Проект по использованию анализу качества воздуха в Москве - детекции аномалий, их кластеризации и предсказания измения концентрации частиц пыли. Данные и результаты анализа отображаются на [web-сайте](http://93.115.20.79/index).

## Источник данных
В проекте используются проекта данные общественного мониторнга воздуха проекта
[Luftdaten](https://luftdaten.info/ "luftdaten.info"). Данные собираются с датчиков концентрации частиц, температуры, атмосферного
давления и влажности воздуха и размещаются в открытом доступе. В Москве установкой станций мониторинга качества воздуха занимаются
волонтеры [breathe.moscov](https://breathe.moscow/ "breathe.moscow").

Информация о погоде в Москве используется по данным метеостанции [Балчуг](https://rp5.ru/%D0%90%D1%80%D1%85%D0%B8%D0%B2_%D0%BF%D0%BE%D0%B3%D0%BE%D0%B4%D1%8B_%D0%B2_%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D0%B5_(%D1%86%D0%B5%D0%BD%D1%82%D1%80,_%D0%91%D0%B0%D0%BB%D1%87%D1%83%D0%B3\) "rp5.ru")  

Для версионирования данных и построения pipline в проекте используется [Data Version Control (DVC)](https://dvc.org/ "Open-source Version Control System for Machine Learning Projects").  

## Docs
### data
[raw_data.rst](docs/data/raw_data.rst)

[dataset.rst](docs/data/dataset.rst)

### api
[api.rst](docs/api/api.rst)
## Notebooks
Выделение и кластеризация аномалий в данных
 
 [Anomaly detection.ipynb](notebooks/Anomaly%20detection.ipynb)
 
 [Linear forecast model on lag features](notebooks/forecasting_sensor_P1.ipynb)

[EDA](notebooks/EDA.ipynb)
