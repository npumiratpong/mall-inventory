from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Union

from .database import engine
from models.schemas import User

def execute_sql_statement(sql_statement, params=None):
    try:
        with engine.connect() as conn:
            result = conn.exec_driver_sql(sql_statement, parameters=params).fetchall()
    except Exception as e:
        print (f"An error occur in query : {e}")
        return None
    return result
    

def get_user_by_username(username: str) -> Dict:
    sql =f"SELECT u.user_id, u.username, u.hashed_password,r.role_name, u.is_active FROM users u " \
         f"INNER JOIN user_mapping um " \
         f"ON u.user_id = um.user_id " \
         f"INNER JOIN roles r " \
         f"ON r.role_id = um.role_id " \
         f"WHERE u.username = %(username)s"

    params = {"username": username}
    
    result = execute_sql_statement(sql, params)
    
    if not result: 
        return None
    else:
        user = {"user_id": result[0][0],
                "username": result[0][1],
                "hashed_password": result[0][2],
                "role": result[0][3],
                "is_active": result[0][4]}    
        return User(**user)

def get_all_items(type: str) -> List:
    sql = f"SELECT DISTINCT {type} FROM products"
    if type:
        response = execute_sql_statement(sql)
    if not response: return []
    else: return [str(x).strip("()',") for x in response]

def get_product_id(barcode_val:Union[int, str] = None, product_name_val:str =None):
    sql = f"SELECT product_id from products"
    where = []
    response = None
    if barcode_val or product_name_val:
        if barcode_val is not None:
            where.append(f"barcode LIKE '%%{barcode_val}%%'")
        if product_name_val is not None:
            where.append(f"product_name='{product_name_val}'")
        if where:
            sql = "{} WHERE {}".format(sql, " AND ".join(v for v in where))
        response = execute_sql_statement(sql)
        print(f"This is reponse after executed {response}")
    if not response: return response
    else: return [x for x in response[0]]

def get_product_by_search_term(search_term:Union[int, str] = None):
    sql = f"SELECT product_id from products"
    where = []
    response = None
    search_term = search_term.strip()
    
    where.append(f"product_id LIKE '%%{search_term}%%'")
    where.append(f"barcode LIKE '%%{search_term}%%'")
    where.append(f"product_name LIKE '%%{search_term}%%'")
    if where:
        sql = "{} WHERE {}".format(sql, " OR ".join(v for v in where))
        response = execute_sql_statement(sql)
    if not response: return response
    else:
        return [str(x).strip("()',") for x in response]
    
def get_product_price_for_mall(product_code: Union[int, str], unit_code:str, customer_name:str):
    if product_code: product_code = product_code.strip()
    if customer_name: customer_name = customer_name.strip()
    if unit_code: unit_code = unit_code.strip()

    sql = f"SELECT `{customer_name}` FROM product_price"
    where = []
    response = 0

    where.append(f"`Item code` = '{product_code}'")
    where.append(f"b_unit='{unit_code}'")

    if where:
        sql = "{} WHERE {}".format(sql, " AND ".join(v for v in where))
        response = execute_sql_statement(sql)

    if response: 
        return [str(x).strip("()',") for x in response]
    return [0]


