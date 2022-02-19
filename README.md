# hothouse

`hothouse` is a Python + PostgreSQL backend for managing and automating climate-controlled environments. I intend to run it on a Raspberry Pi to grow gourmet mushrooms from the comfort of my apartment! Partially inspired by [this wonderful build](https://www.youtube.com/watch?v=z41Wy5ZF4O8) from Kyle Gabriel.

## Prerequisites
- A working installation of PostgreSQL (if you can run the `psql` command line tool, you should be good!)
- A PostgreSQL user + password with `CREATEDB` priveleges
- Basic knowledge of object-oriented programming + Python classes

## Installation
`hothouse` can be installed directly with `pip`:

`pip install git+https://github.com/r1yk/hothouse.git`

## Dependencies
- [SQLAlchemy](https://www.sqlalchemy.org/): this provides an ORM layer so that rows in your Postgres database can easily be accessed/manipulated as Python objects, as opposed to writing raw SQL in your implementation of `hothouse`.
- [pg8000](https://github.com/tlocke/pg8000): My driver-of-choice for connecting SQLAlchemy to your installation of Postgres
- [python-dotenv](https://pypi.org/project/python-dotenv/): This library provides easy access to configuration variables that are stored in a `.env` file at the root of your project 

## Configuration
Access to your instance of Postgres is provided by a `.env` file that you should create in the root of your project. The contents of the file should look like this:
```
PG_HOST=localhost
PG_USERNAME=postgres
PG_PASSWORD=my_postgres_password
DB_NAME=my_postgres_database_name
```
(replace the values with your own settings)

Once you have your Postgres credentials sorted out, import the `hothouse` database schema. Make sure the database you specify with `DB_NAME` has already been created before running this:
```sh
python3 -m hothouse.import_db_schema
```
## Running tests
If you fork `hothouse` and want to run the test suite locally, use the `unittest` module:
```sh
python3 -m unittest discover tests
```

## Implementing your own devices
The key to setting up your own custom environment is writing Python classes that inherit from `hothouse.Device` and `hothouse.Environment`. Here is a simple example that imagines a setup where a light is turned on with a Raspberry Pi by setting a GPIO pin to HIGH:

```python
from datetime import date, time
from hothouse import Device, Environment, Schedule
from hothouse.postgres import get_session
import RPi.GPIO as GPIO


class MyCustomLightFixture(Device):
    # A custom Device needs to implement the `Device._on` and `Device._off` methods.
    gpio_pin_number = 18

    def _on(self):
        GPIO.set(self.gpio_pin_number, GPIO.HIGH)

    def _off(self):
        GPIO.set(self.gpio_pin_number, GPIO.LOW)


class MyCustomEnvironment(Environment):
    # The environment needs to know which class to implement when handling lighting events
    light_class = MyCustomLightFixture


# Create an instance of the custom light class
my_light = MyCustomLightFixture(
    id='my-custom-light-id',
    name='My Custom Light',
    watts=100
)
# Create an instance of the custom environment class
my_environment = MyCustomEnvironment(
    id='my-custom-environment-id',
    name='My Custom Environment',
    light_id=my_light.id
)
# Create a schedule to enforce the desired conditions in the environment
my_schedule = Schedule(
    environment_id=my_environment.id,
    start_at=date.today(),
    light_on_at=time(hour=8),
    light_off_at=time(hour=20)
)

# Create a database session, and commit these records to the database!
with get_session() as session:
    session.add_all(
        [my_light, my_environment, my_schedule]
    )
    session.commit()

# Check in on the new environment every 60 seconds, and let `hothouse` take care of the automations
my_environment.monitor(interval=60)
```