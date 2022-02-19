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