CREATE SCHEMA i7r

CREATE TABLE i7r.devices (
    active boolean,
    voltage NUMERIC,
    watts int
);

CREATE TABLE i7r.humidifiers (
    id char(36) PRIMARY KEY,
    name varchar(80) NOT NULL
) INHERITS (i7r.devices);

CREATE TABLE i7r.lights (
    id char(36) PRIMARY KEY,
    name varchar(80) NOT NULL
) INHERITS (i7r.devices);

CREATE TABLE i7r.heaters (
    id char(36) PRIMARY KEY,
    name varchar(80) NOT NULL
) INHERITS (i7r.devices);

CREATE TABLE i7r.fans (
    id char(36) PRIMARY KEY,
    name varchar(80) NOT NULL
) INHERITS (i7r.devices);

CREATE TABLE i7r.environments (
    id char(36) PRIMARY KEY,
    created_at timestamp,
    fan_id char(36) REFERENCES i7r.fans,
    heater_id char(36) REFERENCES i7r.heaters,
    humidifier_id char(36) REFERENCES i7r.humidifiers,
    humidity_default NUMERIC,
    humidity_tolerance NUMERIC,
    light_id char(36) REFERENCES i7r.lights ON DELETE SET NULL,
    name varchar(80) NOT NULL,
    temp_default NUMERIC,
    temp_tolerance NUMERIC
);

CREATE TABLE i7r.schedules (
    id char(36) PRIMARY KEY,
    environment_id char(36) REFERENCES i7r.environments,
    end_date date,
    fan_on_seconds int,
    fan_off_seconds int,
    light_on_at time,
    light_off_at time,
    start_date date NOT NULL,
    temp NUMERIC,
    humidity NUMERIC
);

CREATE TABLE i7r.readings (
    id char(36) PRIMARY KEY,
    at timestamp NOT NULL,
    environment_id char(36) REFERENCES i7r.environments,
    fan_id char(36) REFERENCES i7r.fans,
    fan_active boolean,
    heater_id char(36) REFERENCES i7r.heaters,
    heater_active boolean,
    humidifier_id char(36) REFERENCES i7r.humidifiers,
    humidifier_active boolean,
    humidity NUMERIC,
    light_id char(36) REFERENCES i7r.lights,
    light_active boolean,
    temp NUMERIC
);