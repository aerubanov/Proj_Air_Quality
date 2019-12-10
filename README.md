[![Build Status](https://travis-ci.org/aerubanov/DS_for_Air.svg?branch=master)](https://travis-ci.org/aerubanov/DS_for_Air)
# DS_for_Air
Проект по использованию Data Scince для анализа качества воздуха в Москве и (в перспективе) предсказания его измения. 

## Источник данных
В проекте используются проекта данные общественного мониторнга воздуха проекта
[Luftdaten](https://luftdaten.info/ "luftdaten.info"). Данные собираются с датчиков концентрации частиц, температуры, атмосферного
давления и влажности воздуха и размещаются в открытом доступе. В Москве установкой станций мониторинга качества воздуха занимаются
волонтеры [breathe.moscov](https://breathe.moscow/ "breathe.moscow").

Для храния данных в проекте используется [Data Version Control](https://dvc.org/ "Open-source Version Control System
for Machine Learning Projects"). Для получения данных после клонирования репозитория выполните
```
pip install dvc
dvc pull
```
