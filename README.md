[![Build Status](https://travis-ci.org/aerubanov/DS_for_Air.svg?branch=master)](https://travis-ci.org/aerubanov/DS_for_Air)
[![codecov](https://codecov.io/gh/aerubanov/DS_for_Air/branch/master/graph/badge.svg)](https://codecov.io/gh/aerubanov/DS_for_Air)
# DS_for_Air
Проект анализу качества воздуха в Москве - детекции аномалий, их кластеризации и предсказания измения концентрации частиц пыли. Данные и результаты анализа отображаются на [web-сайте](http://93.115.20.79/index).
# Docs
### data
[raw_data.rst](docs/data/raw_data.rst)

[dataset.rst](docs/data/dataset.rst)

### api
[api.rst](docs/api/api.rst)
# ML
## Источники данных
В проекте используются проекта данные общественного мониторнга воздуха проекта
[Luftdaten](https://luftdaten.info/ "luftdaten.info"). Данные собираются с датчиков концентрации частиц, температуры, атмосферного
давления и влажности воздуха и размещаются в открытом доступе. В Москве установкой станций мониторинга качества воздуха занимаются
волонтеры [breathe.moscov](https://breathe.moscow/ "breathe.moscow").

Информация о погоде в Москве используется по данным метеостанции [Балчуг](https://rp5.ru/%D0%90%D1%80%D1%85%D0%B8%D0%B2_%D0%BF%D0%BE%D0%B3%D0%BE%D0%B4%D1%8B_%D0%B2_%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D0%B5_(%D1%86%D0%B5%D0%BD%D1%82%D1%80,_%D0%91%D0%B0%D0%BB%D1%87%D1%83%D0%B3\) "rp5.ru")  

Для версионирования данных и построения pipline в проекте используется [Data Version Control (DVC)](https://dvc.org/ "Open-source Version Control System for Machine Learning Projects").  


## Notebooks
Выделение и кластеризация аномалий в данных
 
 [Anomaly detection.ipynb](notebooks/Anomaly%20detection.ipynb)
 
 [Linear forecast model on lag features](notebooks/forecasting_sensor_P1.ipynb)

[EDA](notebooks/EDA.ipynb)

## Загрузка новых данных
- получение списка новых сенсоров
```bash
python -m src.data.get_sensor_list
```
- обновление данных с сенсоров
```bash
python -m src.data.upadate_data
```
- обновление данных метеостанции
```bash
python -m src.data.update_weather
```
## DVC-pipline
<!-- language: lang-none -->
          | DATA/raw/weather |      | DATA/raw/sensors | 
                      *****                   *****                                                
                           ***             ***                           
                              ***       ***                              
                    +-------------------------------+                    
                    | dvc_stages/create_dataset.dvc |                    
                    +-------------------------------+                                                      
                              ***       ***                                                                  
                            ***             *** 
                        *****                   *****                                                                                             
    +-------------------------------+      +---------------------------------+          
    | dvc_stages/train_forecast.dvc |      | dvc_stages/train_clustering.dvc |          
    +-------------------------------+      +---------------------------------+  
                    *                          *                   *
                    *                          *                   * 
                    *                          *                   *
          |models/p1_forecast.obj|     |models/pca.obj|     +----------------------------------+ 
          |models/p2_forecast.obj|     |models/kmean.obj|   | dvc_stages/extract_anomalies.dvc | 
                                                            +----------------------------------+
                                                                            *
                                                                            *
                                                                            *
                                                                |DATA/processed/anomalies.csv| 
<!-- language: lang-none -->
Для запуска стадий pipline используйте dvc repro <stage.dvc> ([подробнее](https://dvc.org/doc/tutorials/pipelines))

# Web
Веб часть проекта состоит из нескольких сервисов, запускаемых docker-compose
 ([docker-compouse.yml](src/web/docker-compose.yml))
 - База данных - PostgresSQL + sqlalchemy
 - loader - загрузка данных с сенсоров и прогноза погоды в БД для обновления данных вреальном времени. Запуск 
  функций загрузки данных с заданным интервалом времени реализован с помощью модуля schedule.
   Для погоды это 1 час, для датчиков 5 минут (они с такой частотой обновляются в источниках).
   Кроме того, осущетвляется загрузка данных с мосэкомониторинга, но они пока сохраняются просто в файл.
 - ml - тут мы берем сохраненые обученные модели (.obj из models/) и периодически их запускаем на поступающих данных.
  Получаем прогноз концентрации частиц и выделенные аномалии с номерами кластеров, к которым они относяться
   и сохраняем в БД. Запуск реализован аналогично loader.
 - script - тут выполняется скрипт, который берет данные из датасета и складывает их в базу данных. Если там 
 уже есть данные для этого промежутка времени, он их перезапишет. Он запускается только один раз после docker-compose
  up. Нужен для того, чтобы когда мы изменим способ сборки датасета или способ выделения аномалий, бд привелась 
  в соответсвие
 - api - на flask реализовано api для получения данных в json из базы ([дока](docs/api/api.rst))
 - web_client - опять же на flask напписан клиент, который через api получает данные и рисует графики.
  Для графиков там [altair](https://altair-viz.github.io/), гененрируется json с данными для графика, который
  уже рендерится на стороне пользователя в браузере