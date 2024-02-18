CREATE TABLE bike_types(
    vehicle_type_id VARCHAR(20) PRIMARY KEY,
    form_factor varchar(20),
    propulsion_type varchar(20),
    max_range_meters FLOAT,
    bike_name VARCHAR(30),
    default_pricing_plan_id VARCHAR(10));