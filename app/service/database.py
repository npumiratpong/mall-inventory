from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import yaml
import os

env = os.environ['TYPE_ENV']
print (env)

config_path = 'service/database_config.yml'

with open(config_path, 'r') as file:
    doc = yaml.load(file, Loader=yaml.FullLoader)

db = doc[env]
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

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()