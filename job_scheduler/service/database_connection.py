from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

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


def execute_sql_statement(sql_statement:str, params: Optional[Dict]=None) -> int:
    with get_conn.connect() as conn:
        result = conn.exec_driver_sql(sql_statement, parameters=params).fetchall()
    return result

def execute_insert_statements_list(sql_statement:str, params: List[Dict], retry:int=0):
    max_retry = 0
    response = None
    try:
        with get_conn(cleanup=False) as conn:
            response = conn.exec_driver_sql(
                                            sql_statement,
                                            params   
                                            )
            conn.commit()
    except (SQLAlchemyError) as ex:
        print (f"Error at SQL : {ex}")
        if retry <= max_retry:
            next_retry = retry + 1
            response = execute_insert_statements_list(sql_statement, params, next_retry)
    return response.rowcount
                                    
def insert_product(params: List[Dict]):
    sql_query = """
                    INSERT INTO products 
                        (product_id, product_name, barcode, created_when) 
                    VALUES (%(product_id)s, %(product_name)s, %(barcode)s, %(created_when)s)
                """
    return execute_insert_statements_list(sql_query, params)