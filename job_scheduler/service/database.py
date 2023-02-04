import contextlib

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

Base = declarative_base()

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:root@localhost/inventory"

db_url = "mysql+pymysql://root:root@localhost/inventory"
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_size=5, pool_recycle=3306)

@contextlib.contextmanager
def get_session(cleanup=False):
    session = Session(bind=engine)
    Base.metadata.create_all(engine)

    try:
        yield session
    except Exception:
        session.rollback()
    finally:
        session.close()

    if cleanup:
        Base.metadata.drop_all(engine)

@contextlib.contextmanager
def get_conn(cleanup=False):
    conn = engine.connect()
    Base.metadata.create_all(engine)

    yield conn
    conn.close()

    if cleanup:
        Base.metadata.drop_all(engine)