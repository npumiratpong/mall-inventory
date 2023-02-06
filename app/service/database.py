from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:root@localhost/inventory"


engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args= dict(host='localhost', port=3306)
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()