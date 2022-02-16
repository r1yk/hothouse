BEGIN;

    -- Add new columns to be populated by existing device children
    ALTER TABLE i7r.devices
        ADD COLUMN id char(36) PRIMARY KEY,
        ADD COLUMN name varchar(80) NOT NULL,
        ADD COLUMN device_type varchar(36);

    -- Set the device_type on all existing children
    UPDATE i7r.lights SET device_type = 'light';
    UPDATE i7r.fans SET device_type = 'fan';
    UPDATE i7r.heaters SET device_type = 'heater';
    UPDATE i7r.humidifiers SET device_type = 'humidifier';

    -- Copy all the child tables into devices 
    INSERT INTO i7r.devices (id, name, device_type, voltage, watts)
        SELECT id, name, device_type, voltage, watts FROM i7r.lights;

    INSERT INTO i7r.devices (id, name, device_type, voltage, watts)
        SELECT id, name, device_type, voltage, watts FROM i7r.fans;

    INSERT INTO i7r.devices (id, name, device_type, voltage, watts)
        SELECT id, name, device_type, voltage, watts FROM i7r.heaters;

    INSERT INTO i7r.devices (id, name, device_type, voltage, watts)
        SELECT id, name, device_type, voltage, watts FROM i7r.humidifiers;

    -- On environments, drop the foreign key constraints that point to the child tables
    ALTER TABLE i7r.environments
        DROP CONSTRAINT environments_light_id_fkey,
        DROP CONSTRAINT environments_fan_id_fkey,
        DROP CONSTRAINT environments_heater_id_fkey,
        DROP CONSTRAINT environments_humidifier_id_fkey;

    -- Add the constraints back, this time pointing to the devices table
    ALTER TABLE i7r.environments
        ADD CONSTRAINT environments_light_id_fkey FOREIGN KEY (light_id) REFERENCES i7r.devices,
        ADD CONSTRAINT environments_fan_id_fkey FOREIGN KEY (fan_id) REFERENCES i7r.devices,
        ADD CONSTRAINT environments_heater_id_fkey FOREIGN KEY (heater_id) REFERENCES i7r.devices,
        ADD CONSTRAINT environments_humidifier_id_fkey FOREIGN KEY (humidifier_id) REFERENCES i7r.devices;

    -- Same thing for foreign key constraints on readings
    ALTER TABLE i7r.readings
        DROP CONSTRAINT readings_light_id_fkey,
        DROP CONSTRAINT readings_fan_id_fkey,
        DROP CONSTRAINT readings_heater_id_fkey,
        DROP CONSTRAINT readings_humidifier_id_fkey;

    ALTER TABLE i7r.readings
        ADD CONSTRAINT readings_light_id_fkey FOREIGN KEY (light_id) REFERENCES i7r.devices,
        ADD CONSTRAINT readings_fan_id_fkey FOREIGN KEY (fan_id) REFERENCES i7r.devices,
        ADD CONSTRAINT readings_heater_id_fkey FOREIGN KEY (heater_id) REFERENCES i7r.devices,
        ADD CONSTRAINT readings_humidifier_id_fkey FOREIGN KEY (humidifier_id) REFERENCES i7r.devices;


    DROP TABLE i7r.lights;
    DROP TABLE i7r.fans;
    DROP TABLE i7r.heaters;
    DROP TABLE i7r.humidifiers;

COMMIT;