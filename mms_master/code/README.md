# comment program version
#### @auther Suraphop Bunsawat

### raspberry pi in center and saperate database in local

1. import node-red in raspberry pi 
mms_pi_center_mssql_local.json

2. restore mssql database in local server
MMS.bak


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
- dialy report
![alt text](https://github.com/NMB-MIC/projects/blob/main/mms_master/pictures/js_daily_report.JPG)
- monthly report
![alt text](https://github.com/NMB-MIC/projects/blob/main/mms_master/pictures/js_monthly_report.JPG)
- show status machines
![alt text](https://github.com/NMB-MIC/projects/blob/main/mms_master/pictures/js_status.JPG)

