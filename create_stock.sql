CREATE TABLE fact_stock(
	station_id INTEGER
	,num_bikes_available INTEGER
	,num_bikes_disabled INTEGER
       ,num_docks_available INTEGER
	,num_docks_disabled INTEGER
	,last_reported varchar(25)
       ,is_charging_station bit
	,status varchar(25)
	,is_installed bit
	,is_renting bit
       ,is_returning bit
	,traffic varchar(50)
	,global_update_time varchar(25)
	,id varchar(50) PRIMARY KEY
);