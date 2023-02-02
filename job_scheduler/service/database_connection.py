from sqlalchemy.orm import Session
from sqlalchemy import text

# from ..models.schemas import product
from .database import get_conn, get_session


from typing import Dict, Union, Optional, List
from sqlalchemy import Column, Integer, String, DateTime

from .database import Base

class product(Base):
    __tablename__ = "products"
    product_id = Column(String(50), primary_key=True)
    product_name = Column(String(255))
    barcode = Column(String(1000))
    created_when = Column(DateTime)


def execute_sql_statement(sql_statement:str, params: Optional[Dict]=None):
    with get_conn.connect() as conn:
        result = conn.exec_driver_sql(sql_statement, parameters=params).fetchall()
    return result
    
def insert_product(data):

    with get_session(cleanup=False) as session:
        session.bulk_insert_mappings(
            product,
            data,
        )
        session.commit()
