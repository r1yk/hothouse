"""Provide access to the SQL backend."""

from ssl import SSLContext
from dotenv import dotenv_values
from pg8000.dbapi import Connection
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session

CONFIG = dotenv_values()
USER = CONFIG['SQL_USER']
PASSWORD = CONFIG['SQL_PASSWORD']
HOST = CONFIG['SQL_HOST']
PORT = CONFIG.get('SQL_PORT', 5432)
DATABASE = CONFIG['SQL_DATABASE']
ENGINE = None

def get_ssl_context(
    certfile: str = 'keys/client-cert.pem',
    keyfile: str = 'keys/client-key.pem',
    cafile: str = 'keys/server-ca.pem'
) -> SSLContext:
    """Return the `SSLContext` for DB connections that require encryption."""
    ssl_context = SSLContext()
    ssl_context.load_cert_chain(certfile=certfile, keyfile=keyfile)
    ssl_context.load_verify_locations(cafile=cafile)
    return ssl_context

def get_connection() -> Connection:
    """Get a DB API `Connection` using the driver of choice (`pg8000` for now)."""
    return Connection(
        user=USER,
        password=PASSWORD,
        host=HOST,
        database=DATABASE,
        ssl_context=get_ssl_context()
    )

def get_engine() -> Engine:
    """Get the running instance of a SQLAlchemy `Engine`."""
    if ENGINE is not None:
        return ENGINE
    return create_engine(
        f"postgresql+pg8000://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}",
        echo=True,
        creator=get_connection
    )

def get_session() -> Session:
    """Get a `session` to maintain database transactions."""
    return sessionmaker(get_engine())
