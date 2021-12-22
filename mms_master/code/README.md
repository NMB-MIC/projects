# Program version
#### @auther Suraphop Bunsawat

## model zoo
- raspberry pi as centerization and saperate database in local server
- raspberry pi only send mqtt to local server

### model raspberry pi as centerization and saperate database in local server

1. import a json file to node-red in raspberry pi
``` 
mms_pi_center_mssql_local.json
```
2. restore the database in local server
```
MMS.bak
```

#### Description

#### insert_data tab
- input 3 signals from plc (running,stop,alarm) to raspberry pi and then sent mqtt
![alt text](https://github.com/NMB-MIC/projects/blob/main/mms_master/pictures/js_input_mqtt.JPG)
- receive mqtt signals and insert data to mssql database
![alt text](https://github.com/NMB-MIC/projects/blob/main/mms_master/pictures/js_insert_data.JPG)
- stamp data for new day at 07:00:00 at lasted status
![alt text](https://github.com/NMB-MIC/projects/blob/main/mms_master/pictures/js_stamp_new_day.JPG)

#### dashboard tab
- show real-time machine status
![alt text](https://github.com/NMB-MIC/projects/blob/main/mms_master/pictures/js_dashboard.JPG)
- daily report
![alt text](https://github.com/NMB-MIC/projects/blob/main/mms_master/pictures/js_daily_report.JPG)
- monthly report
![alt text](https://github.com/NMB-MIC/projects/blob/main/mms_master/pictures/js_monthly_report.JPG)
- show status machines
![alt text](https://github.com/NMB-MIC/projects/blob/main/mms_master/pictures/js_status.JPG)


### raspberry pi only send mqtt to local server
1. import a json file to node-red in raspberry pi
``` 
mms_pi.json
```
2. import a json file to node-red in local server
``` 
mms_local_server.json
```
3. restore the database in local server
```
MMS.bak
```
