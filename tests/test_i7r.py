import unittest
from time import sleep
import os
from uuid import uuid4
from postgres_connector import CONFIG, DATABASE, get_session
from scripts.import_db_schema import import_schema
from i7r import Environment


test_db_name = 'i7r_test_db'


class TestI7R(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Create a transient test database to use during unit tests"""
        os.environ['PGPASSWORD'] = CONFIG['PG_PASSWORD']
        os.system(
            f'psql -U {CONFIG["PG_USERNAME"]} -c "CREATE DATABASE {test_db_name}"')
        import_schema(test_db_name)

    @classmethod
    def tearDownClass(cls):
        """"Drop the transient test database that was originally created"""
        os.system(
            f'psql -U {CONFIG["PG_USERNAME"]} -c "DROP DATABASE {test_db_name}"')

    def test_take_reading(self):
        with get_session(test_db_name) as session:
            pass
