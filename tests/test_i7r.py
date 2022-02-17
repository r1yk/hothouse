import unittest
import os
from uuid import uuid4
from sqlalchemy import select
from postgres_connector import CONFIG, get_session, get_engine
from scripts.import_db_schema import import_schema
from i7r import Device, Environment


test_db_name = 'i7r_test_db'


class TestI7R(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            # Create a transient test database to use during unit tests
            os.environ['PGPASSWORD'] = CONFIG['PG_PASSWORD']
            os.system(
                f'psql -U {CONFIG["PG_USERNAME"]} -c "CREATE DATABASE {test_db_name}"')
            import_schema(test_db_name)

            # Seed the new database with some test data
            with get_session(test_db_name) as session:
                light = Device(
                    id=str(uuid4()),
                    name='Test Light',
                    watts=30
                )

                fan = Device(
                    id=str(uuid4()),
                    name='Test Fan',
                    watts=20
                )

                heater = Device(
                    id=str(uuid4()),
                    name='Test Heater',
                    watts=300
                )

                humidifier = Device(
                    id=str(uuid4()),
                    name='Test Humidifier',
                    watts=100
                )
                session.add_all([light, fan, heater, humidifier])

                environment = Environment(
                    id=str(uuid4()),
                    name='Test Environment',
                    light_id=light.id,
                    fan_id=fan.id,
                    heater_id=heater.id,
                    humidifier_id=humidifier.id
                )
                session.add(environment)

                session.commit()

        except Exception as e:
            """Always run the teardown so a test DB isn't left behind as an artifact"""
            TestI7R.tearDownClass()
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
            environment_query = select(Environment).limit(1)
            environment: Environment = session.execute(
                environment_query).scalars().first()

            environment.take_reading()
