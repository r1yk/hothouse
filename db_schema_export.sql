--
-- PostgreSQL database dump
--

-- Dumped from database version 14.1 (Ubuntu 14.1-2.pgdg20.04+1)
-- Dumped by pg_dump version 14.1 (Ubuntu 14.1-2.pgdg20.04+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: i7r; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA i7r;


ALTER SCHEMA i7r OWNER TO postgres;

--
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: devices; Type: TABLE; Schema: i7r; Owner: postgres
--

CREATE TABLE i7r.devices (
    active boolean,
    voltage numeric,
    watts integer
);


ALTER TABLE i7r.devices OWNER TO postgres;

--
-- Name: environments; Type: TABLE; Schema: i7r; Owner: postgres
--

CREATE TABLE i7r.environments (
    id character(36) NOT NULL,
    created_at timestamp without time zone,
    fan_id character(36),
    heater_id character(36),
    humidifier_id character(36),
    humidity_default numeric,
    humidity_tolerance numeric,
    light_id character(36),
    name character varying(80) NOT NULL,
    temp_default numeric,
    temp_tolerance numeric
);


ALTER TABLE i7r.environments OWNER TO postgres;

--
-- Name: fans; Type: TABLE; Schema: i7r; Owner: postgres
--

CREATE TABLE i7r.fans (
    id character(36) NOT NULL,
    name character varying(80) NOT NULL
)
INHERITS (i7r.devices);


ALTER TABLE i7r.fans OWNER TO postgres;

--
-- Name: heaters; Type: TABLE; Schema: i7r; Owner: postgres
--

CREATE TABLE i7r.heaters (
    id character(36) NOT NULL,
    name character varying(80) NOT NULL
)
INHERITS (i7r.devices);


ALTER TABLE i7r.heaters OWNER TO postgres;

--
-- Name: humidifiers; Type: TABLE; Schema: i7r; Owner: postgres
--

CREATE TABLE i7r.humidifiers (
    id character(36) NOT NULL,
    name character varying(80) NOT NULL
)
INHERITS (i7r.devices);


ALTER TABLE i7r.humidifiers OWNER TO postgres;

--
-- Name: lights; Type: TABLE; Schema: i7r; Owner: postgres
--

CREATE TABLE i7r.lights (
    id character(36) NOT NULL,
    name character varying(80) NOT NULL
)
INHERITS (i7r.devices);


ALTER TABLE i7r.lights OWNER TO postgres;

--
-- Name: readings; Type: TABLE; Schema: i7r; Owner: postgres
--

CREATE TABLE i7r.readings (
    id character(36) NOT NULL,
    at timestamp without time zone NOT NULL,
    environment_id character(36),
    fan_id character(36),
    fan_active boolean,
    heater_id character(36),
    heater_active boolean,
    humidifier_id character(36),
    humidifier_active boolean,
    humidity numeric,
    light_id character(36),
    light_active boolean,
    temp numeric
);


ALTER TABLE i7r.readings OWNER TO postgres;

--
-- Name: schedules; Type: TABLE; Schema: i7r; Owner: postgres
--

CREATE TABLE i7r.schedules (
    id character(36) NOT NULL,
    environment_id character(36),
    end_date date,
    fan_on_seconds integer,
    fan_off_seconds integer,
    light_on_at time without time zone,
    light_off_at time without time zone,
    start_date date NOT NULL,
    temp numeric,
    humidity numeric
);


ALTER TABLE i7r.schedules OWNER TO postgres;

--
-- Name: environments environments_pkey; Type: CONSTRAINT; Schema: i7r; Owner: postgres
--

ALTER TABLE ONLY i7r.environments
    ADD CONSTRAINT environments_pkey PRIMARY KEY (id);


--
-- Name: fans fans_pkey; Type: CONSTRAINT; Schema: i7r; Owner: postgres
--

ALTER TABLE ONLY i7r.fans
    ADD CONSTRAINT fans_pkey PRIMARY KEY (id);


--
-- Name: heaters heaters_pkey; Type: CONSTRAINT; Schema: i7r; Owner: postgres
--

ALTER TABLE ONLY i7r.heaters
    ADD CONSTRAINT heaters_pkey PRIMARY KEY (id);


--
-- Name: humidifiers humidifiers_pkey; Type: CONSTRAINT; Schema: i7r; Owner: postgres
--

ALTER TABLE ONLY i7r.humidifiers
    ADD CONSTRAINT humidifiers_pkey PRIMARY KEY (id);


--
-- Name: lights lights_pkey; Type: CONSTRAINT; Schema: i7r; Owner: postgres
--

ALTER TABLE ONLY i7r.lights
    ADD CONSTRAINT lights_pkey PRIMARY KEY (id);


--
-- Name: readings readings_pkey; Type: CONSTRAINT; Schema: i7r; Owner: postgres
--

ALTER TABLE ONLY i7r.readings
    ADD CONSTRAINT readings_pkey PRIMARY KEY (id);


--
-- Name: schedules schedules_pkey; Type: CONSTRAINT; Schema: i7r; Owner: postgres
--

ALTER TABLE ONLY i7r.schedules
    ADD CONSTRAINT schedules_pkey PRIMARY KEY (id);


--
-- Name: environments environments_fan_id_fkey; Type: FK CONSTRAINT; Schema: i7r; Owner: postgres
--

ALTER TABLE ONLY i7r.environments
    ADD CONSTRAINT environments_fan_id_fkey FOREIGN KEY (fan_id) REFERENCES i7r.fans(id);


--
-- Name: environments environments_heater_id_fkey; Type: FK CONSTRAINT; Schema: i7r; Owner: postgres
--

ALTER TABLE ONLY i7r.environments
    ADD CONSTRAINT environments_heater_id_fkey FOREIGN KEY (heater_id) REFERENCES i7r.heaters(id);


--
-- Name: environments environments_humidifier_id_fkey; Type: FK CONSTRAINT; Schema: i7r; Owner: postgres
--

ALTER TABLE ONLY i7r.environments
    ADD CONSTRAINT environments_humidifier_id_fkey FOREIGN KEY (humidifier_id) REFERENCES i7r.humidifiers(id);


--
-- Name: environments environments_light_id_fkey; Type: FK CONSTRAINT; Schema: i7r; Owner: postgres
--

ALTER TABLE ONLY i7r.environments
    ADD CONSTRAINT environments_light_id_fkey FOREIGN KEY (light_id) REFERENCES i7r.lights(id) ON DELETE SET NULL;


--
-- Name: readings readings_environment_id_fkey; Type: FK CONSTRAINT; Schema: i7r; Owner: postgres
--

ALTER TABLE ONLY i7r.readings
    ADD CONSTRAINT readings_environment_id_fkey FOREIGN KEY (environment_id) REFERENCES i7r.environments(id);


--
-- Name: readings readings_fan_id_fkey; Type: FK CONSTRAINT; Schema: i7r; Owner: postgres
--

ALTER TABLE ONLY i7r.readings
    ADD CONSTRAINT readings_fan_id_fkey FOREIGN KEY (fan_id) REFERENCES i7r.fans(id);


--
-- Name: readings readings_heater_id_fkey; Type: FK CONSTRAINT; Schema: i7r; Owner: postgres
--

ALTER TABLE ONLY i7r.readings
    ADD CONSTRAINT readings_heater_id_fkey FOREIGN KEY (heater_id) REFERENCES i7r.heaters(id);


--
-- Name: readings readings_humidifier_id_fkey; Type: FK CONSTRAINT; Schema: i7r; Owner: postgres
--

ALTER TABLE ONLY i7r.readings
    ADD CONSTRAINT readings_humidifier_id_fkey FOREIGN KEY (humidifier_id) REFERENCES i7r.humidifiers(id);


--
-- Name: readings readings_light_id_fkey; Type: FK CONSTRAINT; Schema: i7r; Owner: postgres
--

ALTER TABLE ONLY i7r.readings
    ADD CONSTRAINT readings_light_id_fkey FOREIGN KEY (light_id) REFERENCES i7r.lights(id);


--
-- Name: schedules schedules_environment_id_fkey; Type: FK CONSTRAINT; Schema: i7r; Owner: postgres
--

ALTER TABLE ONLY i7r.schedules
    ADD CONSTRAINT schedules_environment_id_fkey FOREIGN KEY (environment_id) REFERENCES i7r.environments(id);


--
-- PostgreSQL database dump complete
--

