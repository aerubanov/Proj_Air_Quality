[![Build Status](https://travis-ci.org/aerubanov/Proj_Air_Quality.svg?branch=master)](https://travis-ci.org/aerubanov/Proj_Air_Quality)
[![codecov](https://codecov.io/gh/aerubanov/Proj_Air_Quality/branch/master/graph/badge.svg)](https://codecov.io/gh/aerubanov/Proj_Air_Quality)
# Proj_Air_Quality
Проект анализу качества воздуха в Москве - детекции аномалий, их кластеризации и предсказания измения концентрации частиц пыли. Данные и результаты анализа отображаются на [web-сайте](http://air-quality-moscow.net/). Так же вы можете использовать [Telegram-бот](https://t.me/lskjhgoiuh9887_bot?start=666) для получения информации о концентрации частиц и уведомлений о её измениях.
# Docs
### data
[raw_data.rst](docs/data/raw_data.rst)

[dataset.rst](docs/data/dataset.rst)

# ML
## Источники данных
В проекте используются проекта данные общественного мониторнга воздуха проекта
[Luftdaten](https://luftdaten.info/ "luftdaten.info"). Данные собираются с датчиков концентрации частиц, температуры, атмосферного
давления и влажности воздуха и размещаются в открытом доступе. В Москве установкой станций мониторинга качества воздуха занимаются
волонтеры [breathe.moscov](https://breathe.moscow/ "breathe.moscow").

Информация о погоде в Москве используется по данным метеостанции [Балчуг](https://rp5.ru/%D0%90%D1%80%D1%85%D0%B8%D0%B2_%D0%BF%D0%BE%D0%B3%D0%BE%D0%B4%D1%8B_%D0%B2_%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D0%B5_(%D1%86%D0%B5%D0%BD%D1%82%D1%80,_%D0%91%D0%B0%D0%BB%D1%87%D1%83%D0%B3\) "rp5.ru")  

Для версионирования данных и построения pipline в проекте используется [Data Version Control (DVC)](https://dvc.org/ "Open-source Version Control System for Machine Learning Projects").  


## Загрузка новых данных
- получение списка новых сенсоров
```bash
python -m src.data.get_sensor_list
```
- обновление данных с сенсоров
```bash
python -m src.data.update_data
```
- обновление данных метеостанции
```bash
python -m src.data.update_weather
```
## DVC-pipline
<!-- language: lang-none -->
            +----------------------+                  +----------------------+         
            | DATA/raw/sensors.dvc |                  | DATA/raw/weather.dvc |         
            +----------------------+                  +----------------------+         
             ***                 ***                  ***                  ***         
         ****                       ****          ****                        ***      
      ***                               **      **                               ****  
    ****                           +-----------------+                             ****
         *******                    | extract_sensors |                      *******    
               *******             +-----------------+                ******           
                      ******                 *                 *******                 
                            *******          *          *******                        
                                   ****      *      ****                               
                                    +----------------+                                 
                                    | create_dataset |                                 
                                    +----------------+  

<!-- language: lang-none -->
Для запуска стадий pipline используйте dvc repro <stage.dvc> ([подробнее](https://dvc.org/doc/tutorials/pipelines))



# Tests
* Запуск всех тестов (перед отправкой на PR): `python -m pytest --flake8 -v --cov-report term --cov=./src`
* Запуск единичных тестов: `python -m pytest -vs tests/model/test_extract_anomalies.py::test_main`
