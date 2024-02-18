CREATE TABLE stations(
    station_id INTEGER NOT NULL,
    name varchar(60),
    physical_configuration varchar(30),
    lat FLOAT,
    lon FLOAT,
    altitude FLOAT,
    post_code varchar(10),
    capacity INTEGER,
    is_charging_station integer,
    is_virtual_station bit,
    nearby_distance float,
    _bluetooth_id varchar(5),
    _ride_code_support bit,
    address varchar(60)
    );