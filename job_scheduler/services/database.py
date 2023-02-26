import contextlib
import yaml

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

Base = declarative_base()


config_path = 'services/database_config.yml'

with open(config_path, 'r') as file:
    doc = yaml.load(file, Loader=yaml.FullLoader)

db = doc['develop']
print (db)

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://{}:{}@{}/{}".format(db['username'],
                                                               db['password'],
                                                               db['host'],
                                                               db['db'])

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args= dict(host=db['host'], 
                       port=db['port'],)
)

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