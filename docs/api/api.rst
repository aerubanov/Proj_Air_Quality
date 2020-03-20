************
API methods
************
API methods provide access to data. To use it, you should send http-request on
93.115.20.79:8080. For available options see list bellow:

/sensor_data, method: GET
-------------------------
 JSON
  'start_time': '<iso-format datetime(for example '2020-03-18T09:30:00')>',

  'end_time': '<iso-format datetime>'

 Get all sensor data from time interval between start_time and and time.

/forecast, method: GET
----------------------
 JSON
  optional: 'start_time': '<iso-format datetime>',

  optional: 'end_time': '<iso-format datetime>'

 Get latest available forecast for particles concentration P1 and P2. If start_time
  and end_time arguments passed, all forecasts generated it this time interval return.

/anomaly, method: GET
-----------------------
 JSON
  'start_time': '<iso-format datetime>',

  'end_time': '<iso-format datetime>'

 Get all detected anomalies that fully or partially in range between start_time and end_time.