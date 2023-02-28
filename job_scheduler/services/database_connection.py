from sqlalchemy.exc import SQLAlchemyError
from .database import get_conn, get_session

from typing import Dict, Optional, List
from sqlalchemy import DateTime

def execute_sql_statements(sql_statement:str, params:Optional[None] = None, retry:int=0):
    max_retry = 10
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
            response = execute_sql_statements(sql_statement, params, next_retry)
    return response.rowcount
                                    
def insert_product(params: List[Dict]):
    sql_query = """
                    INSERT INTO products 
                        (product_id, product_name, barcode, created_when) 
                    VALUES (%(product_id)s, %(product_name)s, %(barcode)s, %(created_when)s)
                """
    return execute_sql_statements(sql_query, params)

def delete_product(params: DateTime):
    sql = f"DELETE FROM products WHERE created_when < '{params}'"
    return execute_sql_statements(sql)