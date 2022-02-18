import unittest
from unittest.mock import Mock
from datetime import datetime, date, time
import os
from uuid import uuid4
from sqlalchemy import select
from scripts.import_db_schema import import_schema
from hothouse import Schedule, Device
from mocks.mock_hothouse import MockEnvironment, MockLight, MockFan, MockHeater, MockHumidifier
from hothouse.postgres import CONFIG, get_engine, get_session
test_db_name = 'hothouse_test_db'


class TestHothouse(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            print('Setting up...')
            # Create a transient test database to use during unit tests
            os.environ['PGPASSWORD'] = CONFIG['PG_PASSWORD']
            os.system(
                f'psql -U {CONFIG["PG_USERNAME"]} -c "CREATE DATABASE {test_db_name}"')
            import_schema(test_db_name)

            # Seed the new database with some test data
            with get_session(test_db_name) as session:
                light = MockLight(
                    id=str(uuid4()),
                    name='Test Light',
                    watts=30
                )

                fan = MockFan(
                    id=str(uuid4()),
                    name='Test Fan',
                    watts=20
                )

                heater = MockHeater(
                    id=str(uuid4()),
                    name='Test Heater',
                    watts=300
                )

                humidifier = MockHumidifier(
                    id=str(uuid4()),
                    name='Test Humidifier',
                    watts=100
                )
                session.add_all([light, fan, heater, humidifier])

                environment = MockEnvironment(
                    id=str(uuid4()),
                    name='Test Environment',
                    light_id=light.id,
                    fan_id=fan.id,
                    heater_id=heater.id,
                    humidifier_id=humidifier.id
                )
                session.add(environment)

                schedule = Schedule(
                    id=str(uuid4()),
                    environment_id=environment.id,
                    temp=70,
                    humidity=0.5,
                    fan_on_seconds=60,
                    fan_off_seconds=3540,
                    start_date=date.today(),
                    light_on_at=time(hour=8),
                    light_off_at=time(hour=20)
                )
                session.add(schedule)

                session.commit()

        except Exception as e:
            """Always run the teardown so a test DB isn't left behind as an artifact"""
            TestHothouse.tearDownClass()
            raise e

    @classmethod
    def tearDownClass(cls):
        print('Tearing down...')
        try:
            # Get rid of the SQLAlchemy engine that's managing connections
            get_engine(test_db_name).dispose()

            # Drop the transient test database that was originally created
            os.system(
                f'psql -U {CONFIG["PG_USERNAME"]} -c "DROP DATABASE {test_db_name}"')

        except Exception as e:
            print('Teardown failed!', e)

    def test_take_reading(self):
        with get_session(test_db_name) as session:
            environment_query = select(MockEnvironment).limit(1)
            environment: MockEnvironment = session.execute(
                environment_query).scalars().first()

        # Mock up some return values for temp and humidity
        MockEnvironment.get_temp = Mock(return_value=70)
        MockEnvironment.get_humidity = Mock(return_value=0.5)

        # Take a reading at 8:00am today
        environment.take_reading(
            at=datetime.now().replace(hour=8, minute=0, second=0))

        with get_session(test_db_name) as session:
            heater: Device = session.get(Device, environment.heater_id)
            humidifier: Device = session.get(Device, environment.heater_id)
            fan: Device = session.get(Device, environment.fan_id)
            light: Device = session.get(Device, environment.light_id)

            # Comfortable conditions, no heat/humidity needed
            self.assertFalse(heater.active)
            self.assertFalse(humidifier.active)

            # Light should turn on at 8am
            self.assertTrue(light.active)
            # Fan should be on for the first 60 seconds of the hour
            self.assertTrue(fan.active)

        # Take a reading at 8:01am today, fan should have turned off after 60 seconds
        environment.take_reading(at=datetime.now().replace(hour=8, minute=1))
        with get_session(test_db_name) as session:
            fan: Device = session.get(Device, environment.fan_id)
            self.assertFalse(fan.active)

        # Take a reading at 9:00am today, fan should come back on for the first 60 seconds of the hour
        environment.take_reading(
            at=datetime.now().replace(hour=9, minute=0))
        with get_session(test_db_name) as session:
            fan: Device = session.get(Device, environment.fan_id)
            self.assertTrue(fan.active)

        # Take a reading at 11:00pm, make sure the light turned itself off
        environment.take_reading(
            at=datetime.now().replace(hour=23, minute=0))
        with get_session(test_db_name) as session:
            light: Device = session.get(Device, environment.light_id)
            self.assertFalse(light.active)

        # Drop the temp below the allowable threshold, make sure the heat comes on
        MockEnvironment.get_temp = Mock(return_value=65)
        environment.take_reading()
        with get_session(test_db_name) as session:
            heater: Device = session.get(Device, environment.heater_id)
            self.assertTrue(heater.active)

        # Increase the temp over the allowable threshold, make sure the heat turns off
        MockEnvironment.get_temp = Mock(return_value=75)
        environment.take_reading()
        with get_session(test_db_name) as session:
            heater: Device = session.get(Device, environment.heater_id)
            self.assertFalse(heater.active)

        # Drop the humidity too low and make sure humidifier comes on
        MockEnvironment.get_humidity = Mock(return_value=0.3)
        environment.take_reading()
        with get_session(test_db_name) as session:
            humidifier: Device = session.get(Device, environment.humidifier_id)
            self.assertTrue(humidifier.active)

        # Increase the humidity and make sure humidifier turns off
        MockEnvironment.get_humidity = Mock(return_value=0.7)
        environment.take_reading()
        with get_session(test_db_name) as session:
            humidifier: Device = session.get(Device, environment.humidifier_id)
            self.assertFalse(humidifier.active)
